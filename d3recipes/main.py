"""
# How to make a JSZip compatible zipfile (not just a zip)
zipfilename = "zipfile"
mf = StringIO()
with zipfile.ZipFile(mf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr(zipfilename, code)
zipdata = mf.getvalue().encode("base64")

# And how to unzip it
code = zipfile.ZipFile(StringIO(b64.decode("base64"))).open(zipfilename).read()

"""
#!/usr/bin/env python
from __future__ import print_function
import webapp2
import os, os.path
import json
import logging
import time
import random
import zipfile
import binascii
try: from cStringIO import StringIO
except: from StringIO import StringIO
import config

from google.appengine.ext.webapp import template, util
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import search

from identitytoolkit import gitkitclient

#-----------------------------------------------------------------------------------------

ltrs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_b64_length = 100000 # 100kb of code
zipfilename = 'zipfile'
S3_URL_UP = "https://s3.amazonaws.com/chartrecipesupload"
S3_URL_DN = "https://s3.amazonaws.com/chartrecipesoutput"

IS_LOCAL = False
if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
    IS_LOCAL = True
    logging.debug("[*] Local server info activated")
    S3_URL_UP = S3_URL_UP.replace("https://", "http://")
    S3_URL_DN = S3_URL_DN.replace("https://", "http://")

# Note localhost must be http while the real appspot app can be https
server = "http://localhost:12080" if IS_LOCAL else "https://d3recipes.appspot.com"
auth_dir = "auth_local" if IS_LOCAL else "auth"


global_template = {"server":server, "zipfilename":zipfilename, 
                   "max_b64_length":max_b64_length, "S3_URL_UP":S3_URL_UP,
                   "S3_URL_DN":S3_URL_DN}

gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(auth_dir+'/gitkit-server-config.json')

#-----------------------------------------------------------------------------------------

class User(ndb.Model):
    date          = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    display_name  = ndb.StringProperty(indexed=False, default='')
    recipes       = ndb.TextProperty(indexed=False, default='[]') # save on indexing
    liked_recipes = ndb.TextProperty(indexed=False, default='[]')


class Recipe(ndb.Model):
    date      = ndb.DateTimeProperty(auto_now_add=True, indexed=True) # index sort by date
    meta      = ndb.TextProperty(indexed=True, default='') # index makes it searchable?
    b64       = ndb.TextProperty(indexed=False, default='') # blob
    user      = ndb.KeyProperty(indexed=True, kind=User) # index allows find-by-user
    thumbnail = ndb.TextProperty(indexed=False)
    num_likes = ndb.IntegerProperty(indexed=True, default=0) # index to sort by likes
    
    @classmethod
    def most_recent(cls, n_latest=10):
        return cls.query().order(-cls.date).fetch(n_latest)

    @classmethod
    def most_liked(cls, n_latest=10):
        return cls.query(cls.num_likes>0).order(-cls.num_likes).fetch(n_latest)
    
    @classmethod
    def by_user(cls, _user, n_latest=20):
        return cls.query(Recipe.user==_user.key).order(-cls.date).fetch(n_latest)

    # Enable full text search
    # https://cloud.google.com/appengine/training/fts_intro/lesson2
    # https://cloud.google.com/appengine/articles/deferred
    # http://sookocheff.com/posts/2015-02-23-syncing-search-documents-with-datastore-entities/
    # Technically this could lead to inconsistencies in the index (see link above)
    @classmethod
    def put_search_document(cls, recipe_id):
        model = ndb.Key(cls, recipe_id).get()
        if model:
            meta = json.loads(model.meta)
            document = search.Document(
                doc_id = recipe_id,
                fields=[
                   search.TextField(name='recipe_title', value=meta['recipe_title']),
                   search.TextField(name='recipe_description', value=meta['recipe_description']),
                   ])
            index = search.Index(name="recipemeta")
            index.put(document)
    
    def _post_put_hook(self, future):
        logging.info("START Q {}".format(self.key.id()))
        deferred.defer(Recipe.put_search_document,
                       self.key.id(),
                       _transactional=ndb.in_transaction())


#-----------------------------------------------------------------------------------------

def _get_or_create_user_from_id(user_id, display_name=''):
    user = ndb.Key(User, user_id).get()
    if user is None:
        user = User(id=user_id, display_name=display_name) # leave everything else default
        user.put()
        return user
    else:
        return user


def _get_gitkit_user(request):
    """gitkit_token only includes the bare minumum: user_id mainly
    gitkit_user includes that plus name and photo:
    {'photo_url': u'photo.jpg', 'user_id': u'1', 'email': u'm@gmail.com', 
    'email_verified': True, 'provider_info': [{u'photoUrl': u'photo.jpg?sz=50', 
    u'displayName': u'a b', u'providerId': u'google.com', u'federatedId': u'https://1'}], 
    'salt': None, 'name': u'mega fauna', 'provider_id': None, 'password_hash': None}
    """
    
    if 'gtoken' not in request.cookies:
        logging.error("gitkit_user is None. No gtoken in request.cookies")
        return None
    
    gtoken = request.cookies['gtoken']
    
    try:
        gitkit_token = gitkit_instance.VerifyGitkitToken(request.cookies['gtoken'])
        gitkit_user = gitkit_instance.GetUserById(gitkit_token.user_id)
    except Exception as e:
        logging.error("gitkit_user is None. VerifyGitkitToken Exception {}".format(e))
        return None

    logging.info("gitkit_user {} {}".format(str(vars(gitkit_token)), str(vars(gitkit_user))))

    if gitkit_user:
        return gitkit_user
    else:
        logging.error("gitkit_user is None.")
        return None


def get_or_create_user(request):
    """If I am a new user, then create a User entry.
    If I am logged in, then return a User, otherwise return None."""
    gitkit_user = _get_gitkit_user(request)
    
    if gitkit_user is not None:
        user = _get_or_create_user_from_id(gitkit_user.user_id, 
                                           gitkit_user.provider_info[0]['displayName'])
        userstr = str(vars(gitkit_user))
    else:
        gitkit_user, user, userstr = None, None, ''
    
    return gitkit_user, user, userstr


def _json_to_zipped_b64(json):
    mf = StringIO()
    with zipfile.ZipFile(mf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zipfilename, json)
    return mf.getvalue().encode("base64")


#-----------------------------------------------------------------------------------------
            
class SaveHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("SaveHandler :: start")
        
        # If I am not logged in, then return None
        gitkit_user, user, userstr = get_or_create_user(self.request)
        
        if user is None:
            r = {"status_code":200, "loggedin":0}
            self.response.write(json.dumps(r))
            return
        
        meta_json          = self.request.get("meta_json")
        state_json_b64     = self.request.get("state_json_b64")
        thumbnail_data_url = self.request.get("thumbnail_data_url")
        print("meta", meta_json, state_json_b64, "end")
        
        try:
            meta = json.loads(meta_json)
        except ValueError:
            self.response.headers.add_header('Content-Type', 'application/json')
            r = {"status_code":400, "error":"Error with uploaded parameters"}
            self.response.write(json.dumps(r))
            return
        
        if "recipe_id" not in meta:
            self.response.headers.add_header('Content-Type', 'application/json')
            r = {"status_code":400, "error":"Your parameters are corrupted (no recipe_id)"}
            self.response.write(json.dumps(r))
            return
        
        if len(state_json_b64) > max_b64_length or len(meta) > max_b64_length or len(state_json_b64) <= 16:
            self.response.headers.add_header('Content-Type', 'application/json')
            r = {"status_code":400, "error":"Your code is too long or too short"}
            self.response.write(json.dumps(r))
            return
        
        #---------------------------------------------------------------------------------
        # recipe_id is the user's name for the recipe
        # uniq_random_id = binascii.hexlify(os.urandom(8)) # 16 chars
        #
        #if "username" in meta and meta["username"]: username = meta["username"]
        #else: username = ''.join(random.choice(ltrs) for _ in range(8))
        
        recipe_id = meta['recipe_id']
        recipe = ndb.Key(Recipe, recipe_id).get()
        if recipe is None:
            recipe = Recipe(id=recipe_id, 
                            user=ndb.Key(User, gitkit_user.user_id), 
                            meta=meta_json, 
                            b64=state_json_b64,
                            thumbnail=thumbnail_data_url)
        else:
            # update the recipe details, but first check that i own it
            is_recipe_owner = True if recipe.user == user.key else False
            if is_recipe_owner is False:
                r = {"status_code":400, "error":"You do not own this recipe!"}
                self.response.write(json.dumps(r))
                return
            
            recipe.meta      = meta_json
            recipe.b64       = state_json_b64
            recipe.thumbnail = thumbnail_data_url
        recipe.put()
        
        user_recipes = json.loads(user.recipes) if user.recipes != '' else []
        if recipe_id not in user_recipes:
            user_recipes.append(recipe_id)
        user.recipes = json.dumps(user_recipes)
        user.put()
        
        
        #---------------------------------------------------------------------------------
        # Finally, respond
        #
        recipe_url = server + "/recipe/" + recipe_id
        self.response.headers.add_header('Content-Type', 'application/json')
        r = {"status_code":200, "loggedin":1, "recipe_url":recipe_url}
        self.response.write(json.dumps(r))
        return


class ShowChartHandler(webapp2.RequestHandler):
    def get(self, recipe_id=None, chart_id=None):
        pass


class SignInHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), "signin.html")
        self.response.out.write(template.render(path, global_template))


class ShowRecipeHandler(webapp2.RequestHandler):
    def get(self, recipe_id=None):
        mode = "RECIPE"
        
        recipe = ndb.Key(Recipe, recipe_id).get() if recipe_id is not None else None
        gitkit_user, user, userstr = get_or_create_user(self.request)
        
        if recipe is None:
            self.abort(404)
            return
        
        meta_json = recipe.meta
        state_json_b64 = recipe.b64
                
        if user is None:
            is_recipe_owner = False
            is_liked_recipe = False
        else:
            is_recipe_owner = True if recipe.user == user.key else False
            is_liked_recipe = True if recipe.key.id() in json.loads(user.liked_recipes) else False
        
        path = os.path.join(os.path.dirname(__file__), "index.html")
        d_template = dict(global_template)
        d_template.update({"mode":mode, 
                           "userstr":userstr,
                           "meta_json":json.dumps(meta_json), 
                           "recipe_id":recipe_id,
                           "num_likes":recipe.num_likes,
                           "is_recipe_owner":int(is_recipe_owner),
                           "is_liked_recipe":int(is_liked_recipe),
                           "is_logged_in":int(user is not None),
                           "state_json_b64":state_json_b64})
        self.response.out.write(template.render(path, d_template))
        return


class EditRecipeHandler(webapp2.RequestHandler):
    def get(self, recipe_id=None):
        mode = "EDIT"
        
        recipe = ndb.Key(Recipe, recipe_id).get() if recipe_id is not None else None
        gitkit_user, user, userstr = get_or_create_user(self.request)
        
        if recipe is None:
            # New recipe with example! Example recipes should be selected from a dropdown
            import exampledata, random
            state_json_b64 = _json_to_zipped_b64(random.choice(exampledata.states_json))
            
            is_recipe_owner = False
            is_liked_recipe = False
            userstr = '' # debug
            recipe_id = recipe_id or ''
            meta_json = '{}'
        else:
            state_json_b64 = recipe.b64
            
            # Check if I am the owner, otherwise fork to a new recipe
            if user is None:
                is_recipe_owner = False
                is_liked_recipe = False
            else:
                is_recipe_owner = True if recipe.user == user.key else False
                is_liked_recipe = True if recipe.key.id() in json.loads(user.liked_recipes) else False
            
            meta_json = recipe.meta
            logging.info("meta_json {} {}".format(recipe, meta_json))
        
        path = os.path.join(os.path.dirname(__file__), "index.html")
        d_template = dict(global_template)
        d_template.update({"mode":mode, 
                           "meta_json":json.dumps(meta_json), 
                           "is_recipe_owner":int(is_recipe_owner),
                           "is_liked_recipe":int(is_liked_recipe),
                           "is_logged_in":int(user is not None),
                           "recipe_id":recipe_id,
                           "userstr":userstr,
                           "state_json_b64":state_json_b64.replace("\n","")})
        self.response.out.write(template.render(path, d_template))
        return


class LikeRecipeHandler(webapp2.RequestHandler):
    def post(self):
        recipe_id = self.request.get('recipe_id')
        if recipe_id == '':
            r = {"status_code":400, "error":"No recipe information supplied!"}
            self.response.write(json.dumps(r))
            return
        
        recipe = ndb.Key(Recipe, recipe_id).get()
        if recipe is None:
            r = {"status_code":400, "error":"No recipe with this id found!"}
            self.response.write(json.dumps(r))
            return
        
        gitkit_user, user, userstr = get_or_create_user(self.request)
        if user is None:
            r = {"status_code":400, "error":"You must be logged in to like a recipe!"}
            self.response.write(json.dumps(r))
            return
        
        #------------------------
        # Like OR unlike a recipe
        #
        liked_recipes = json.loads(user.liked_recipes)
        if recipe_id in liked_recipes:
            liked_recipes.remove(recipe_id)
            like_change = -1
            message = "You unliked recipe {}".format(recipe_id)
        else:
            liked_recipes.append(recipe_id)
            like_change = 1
            message = "You liked recipe {}".format(recipe_id)
        
        recipe.num_likes = recipe.num_likes + like_change
        recipe.put()
        user.liked_recipes = json.dumps(liked_recipes)
        user.put()
        
        r = {"status_code":200, "message":message, "num_likes":recipe.num_likes, 
             "like_change":like_change}
        self.response.write(json.dumps(r))
        return


def fix_searchquery(searchquery):
    """Attempt to hack around google's terrible fulltext system
    """
    mod_searchquery = ' '.join(['~{}'.format(s) for s in searchquery.split()])
    mod_searchquery = '"' + mod_searchquery.replace('"', '\\"') + '"'
    return mod_searchquery
    
class BrowseRecipesHandler(webapp2.RequestHandler):
    def get(self):
        def _recipes_to_json(_recipes):
            return json.dumps(
                [{"meta":r.meta,
                  "num_likes":r.num_likes,
                  "thumbnail":r.thumbnail}
                 for r in _recipes], ensure_ascii=False)
        
        limit_liked_recipes = 10
        limit_search_results = 10
        limit_most_recent = 10
        limit_most_liked = 10
        # each of these can be empty
        search_recipes_json = user_recipes_json = liked_recipes_json = "[]"
        
        searchquery = self.request.get("searchquery")
        
        gitkit_user, user, userstr = get_or_create_user(self.request)
        
        if searchquery != '':
            index = search.Index(name="recipemeta")
            mod_searchquery = fix_searchquery(searchquery)
            logging.info("searchquery {} {}".format(searchquery, mod_searchquery))
            
            full_query = search.Query(query_string=mod_searchquery, 
                options=search.QueryOptions(limit=limit_search_results))
            search_results = index.search(full_query)
            logging.info("found {} results".format(search_results.number_found))
            search_recipes = ndb.get_multi([ndb.Key(Recipe,doc.doc_id) for doc in search_results])
            search_recipes_json = _recipes_to_json(search_recipes)
        
        if user is not None:
            user_recipes = Recipe.by_user(user)
            user_recipes_json = _recipes_to_json(user_recipes)
            
            liked_recipes = ndb.get_multi([ndb.Key(Recipe, k) for k in json.loads(user.liked_recipes)[:limit_liked_recipes]])
            liked_recipes_json = _recipes_to_json(liked_recipes)
        
        most_recent_recipes = Recipe.most_recent(n_latest=limit_most_recent)
        most_recent_recipes_json = _recipes_to_json(most_recent_recipes)
        
        most_liked_recipes = Recipe.most_liked(n_latest=limit_most_liked)
        most_liked_recipes_json = _recipes_to_json(most_liked_recipes)
        
        path = os.path.join(os.path.dirname(__file__), "browse.html")
        d_template = dict(global_template)
        d_template.update({"liked_recipes_json":liked_recipes_json,
                           "search_recipes_json":search_recipes_json,
                           "user_recipes_json":user_recipes_json,
                           "most_liked_recipes_json":most_liked_recipes_json,
                           "most_recent_recipes_json":most_recent_recipes_json})
        self.response.out.write(template.render(path, d_template))
        return


app = webapp2.WSGIApplication([
    ('/oauth2callback', SignInHandler),
    ('/save', SaveHandler),
    ('/recipe/(.*)', ShowRecipeHandler),
    ('/recipe/(.*)/(.*)', ShowChartHandler),
    ('/edit/(.*)', EditRecipeHandler),
    ('/edit', EditRecipeHandler),
    ('/like', LikeRecipeHandler),
    ('/search', BrowseRecipesHandler),
    ('/', BrowseRecipesHandler)
], debug=True)
