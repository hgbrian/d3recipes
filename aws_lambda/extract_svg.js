//
// Given a webpage, extract the first svg element
// phantomjs extract_svg.js http://localhost:12080
// Or extract by elementID
// phantomjs extract_svg.js http://localhost:12080 mysvgid
//

var system = require('system');
 
if (system.args.length != 2) {
    console.log("Usage: extract.js  ");
    phantom.exit(1);
}

var address = system.args[1];
var elementID = "not in use"; //system.args[2];

var page = require('webpage').create();
 
function prependChild(someParentObject, someChildObject) {
    someParentObject.insertBefore(someChildObject,someParentObject.firstChild);
}

function serialize(elementID) {
    var serializer = new XMLSerializer();
    //var element = document.getElementById(elementID);
    var element = document.getElementsByTagName("svg")[0];

    //------------------------------------------------------------------------------------
    // Make sure the svg works as a standalone file by adding the namespace
    //
    if (element.getAttribute("xmlns") == undefined || element.getAttribute("xmlns") == "" || element.getAttribute("xmlns") == null) {
        var att1 = document.createAttribute("xmlns");
        att1.value = "http://www.w3.org/2000/svg";
        element.setAttributeNode(att1);
        var att2 = document.createAttribute("xmlns:xlink");
        att2.value = "http://www.w3.org/1999/xlink";
        element.setAttributeNode(att2);
    }
    
    //--------------------------------
    // Add in all html styles in order
    //    
    var styles = document.getElementsByTagName("style");
    var styles_text = '';
    for (var i=0; i<styles.length; i++) {
        if (styles[i] != undefined) {
            styles_text = styles_text + styles[i].innerHTML;
        }
    }
    
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    //element.appendChild(defs);
    element.insertBefore(defs, element.firstChild);
    
    var style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    defs.appendChild(style);
    var node = document.createTextNode(styles_text);
    style.appendChild(node);

    return serializer.serializeToString(element);
}
 
function extract(elementID, timeout) {
  return function(status) {
    if (status != 'success') {
      console.log("Failed to open the page.");
    } else {
      window.setTimeout(function() {
          var output = page.evaluate(serialize, elementID);
          console.log(output);    
          phantom.exit();
      }, timeout);
    }
  };
}

// Use a timeout if there is a delay in constructing the svg
var timeout = 0;
page.open(address, extract(elementID, timeout));
