//
// Given a webpage, extract the first svg element
// phantomjs extract_svg.js http://localhost:12080 outname
//

var system = require('system');
var fs = require('fs');
 
if (system.args.length != 3) {
    console.log("Usage: extract.js <html_file> <outname>");
    phantom.exit(1);
}

var address = system.args[1];
var outname = system.args[2];
var OUTPUT_PNG = true;

var page = require('webpage').create();
 
function prependChild(someParentObject, someChildObject) {
    someParentObject.insertBefore(someChildObject,someParentObject.firstChild);
}

function serializeSVG() {
    var serializer = new XMLSerializer();
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
    
    //------------------------------------------------------------------------------------
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
    
    var clipRect = document.querySelector("svg").getBoundingClientRect();
    return [serializer.serializeToString(element), clipRect];
}

function extract(outname) {
  return function(status) {
    if (status != 'success') {
      console.log("Failed to open the page.");
    } 
    else {
      var outputs = page.evaluate(serializeSVG);
      var output = outputs[0];
      var clipRect = outputs[1];
      
      //------------------------------------------------------------------------------------
      // Write results to SVG and PNG. Why is this not writeFile? It's not node.js...
      // http://phantomjs.org/api/fs/method/write.html
      //
      console.log(fs);
      fs.write(outname+'.svg', output, function(err) {
          if(err) { console.log(err); }
          else { console.log("The file was saved!"); }
      });

      if (OUTPUT_PNG) {
          // Does not include the blank parts of the SVG. This could be good or bad.
          page.clipRect = {
              top:    clipRect.top,
              left:   clipRect.left,
              width:  clipRect.width,
              height: clipRect.height
          };

          page.render(outname+'.png');
      }
            
      phantom.exit();
    }
  };
}

page.open(address, extract(outname));
