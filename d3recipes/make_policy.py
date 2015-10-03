# http://bencoe.tumblr.com/post/30685403088/browser-side-amazon-s3-uploads-using-cors
# http://stackoverflow.com/questions/11240127/uploading-image-to-amazon-s3-with-html-javascript-jquery-with-ajax-request-n
# http://awspolicygen.s3.amazonaws.com/policygen.html
# IAM gives me the arn for this user arn:aws:iam::319133706199:user/stereogram
# More on ARN format http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html

import hmac, hashlib, base64, json, re

POLICY_JSON = '''{ "expiration": "2040-12-01T12:00:00.000Z",
            "conditions": [
            {"bucket": "chartrecipesupload"},
            ["starts-with", "$key", ""],
            {"acl": "private"},                           
            ["starts-with", "$Content-Type", ""],
            ["content-length-range", 0, 8000000]
            ]
          }'''

_, aws_access_key, aws_secret_key = open("chartrecipesuser_credentials.csv").readlines()[1].strip().split(',')

pat = re.compile(r'\s+')
pol = base64.b64encode(pat.sub('',POLICY_JSON))
sig = base64.b64encode(hmac.new(aws_secret_key, pol, hashlib.sha1).digest())

print "Generated policy".center(100,"-"), "\n", pol
print "Generated policy signature".center(100,"-"), "\n", sig
