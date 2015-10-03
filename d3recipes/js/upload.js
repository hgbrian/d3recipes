var UPLOAD = (function() { var upload = {};

//
// Note policy is tied to the S3 bucket, so giving an S3 bucket as a parameter 
// does not make sense
//

function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0 ; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    return new Blob(byteArrays, { type: contentType });
}

upload.uploadB64Blob = function(b64blob) {
    var prefix = "data:image/png;base64,";
    if (b64blob.substr(0,prefix.length) != prefix) { alert("ERROR! Wrong filetype"); }
    b64blob = b64blob.substr(prefix.length);
        
    var randk = Math.floor((Math.random() * 1000));
    var datek = ((new Date).getTime()).toString().slice(4)
    var key = datek + randk + '.png';
    var blob = base64toBlob(b64blob, "image/png");
    
    var fd = new FormData();
    fd.append('key', key);
    fd.append('acl', 'private');
    fd.append('Content-Type', "image/png");
    fd.append('AWSAccessKeyId', 'AWS1');
    fd.append('policy', 'AWS3');
    fd.append('signature','AWS4');
    //fd.append("file",file);
    fd.append("file",blob);
    
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.addEventListener("error", uploadFailed, false);
    xhr.addEventListener("abort", uploadCanceled, false);
    
    xhr.open('POST', 'https://chartrecipesupload.s3.amazonaws.com/', true); //MUST BE LAST LINE BEFORE YOU SEND
    xhr.send(fd);
    
    return key;
  }

upload.uploadHTML = function(s3_key, html) {
    //var datek = ((new Date).getTime()).toString().slice(6)
    
    var key = s3_key + '.html';
    
    var fd = new FormData();
    fd.append('key', key);
    fd.append('acl', 'private');
    fd.append('Content-Type', "text/html");
    fd.append('AWSAccessKeyId', 'AWS1');
    fd.append('policy', 'AWS3');
    fd.append('signature','AWS4');
    //fd.append("file",file);
    fd.append("file",html);
    
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.addEventListener("error", uploadFailed, false);
    xhr.addEventListener("abort", uploadCanceled, false);
    
    xhr.open('POST', 'https://chartrecipesupload.s3.amazonaws.com/', true); //MUST BE LAST LINE BEFORE YOU SEND
    xhr.send(fd);
    
    return true;
  }

upload.uploadFile = function() {
    var file = document.getElementById('file').files[0];
    var fd = new FormData();
    
    var key = (new Date).getTime() + '-' + file.name;
    
    fd.append('key', key);
    fd.append('acl', 'private');
    fd.append('Content-Type', file.type);
    fd.append('AWSAccessKeyId', 'AWS1');
    fd.append('policy', 'AWS3');
    fd.append('signature','AWS4');
    fd.append("file",file);
    
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.addEventListener("error", uploadFailed, false);
    xhr.addEventListener("abort", uploadCanceled, false);
    
    xhr.open('POST', 'https://chartrecipesupload.s3.amazonaws.com/', true); //MUST BE LAST LINE BEFORE YOU SEND
    xhr.send(fd);
  }

  function uploadProgress(evt) {
    if (evt.lengthComputable) {
      var percentComplete = Math.round(evt.loaded * 100 / evt.total);
      //document.getElementById('progressNumber').innerHTML = percentComplete.toString() + '%';
    }
    else {
      //document.getElementById('progressNumber').innerHTML = 'unable to compute';
    }
  }

  function uploadComplete(evt) {
    /* This event is raised when the server send back a response */
    // alert(" Uploaded! " + evt.target.responseText );
  }

  function uploadFailed(evt) {
    alert("There was an error attempting to upload the file." + evt);
  }

  function uploadCanceled(evt) {
    alert("The upload has been canceled by the user or the browser dropped the connection.");
  }
  
return upload; })(UPLOAD || {});
