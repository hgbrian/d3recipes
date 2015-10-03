var async = require('async');
var AWS = require('aws-sdk');
var util = require('util');
var spawn = require('child_process').spawn;
var fs = require('fs');

var s3 = new AWS.S3();

// globals
var in_bucket  = "chartrecipesupload";
var out_bucket = "chartrecipesoutput";

//var povray_exe = spawn('./povray', ['/tmp/stdin.pov', '-w300', '-h300', '-O-']);
//var povray_content_type = "content-type:image/PNG";
//var povray_data_type = "binary";


exports.handler = function(event, context) {
    console.log("Reading options from event:\n", util.inspect(event, {depth: 5}));
    var srcBucket = event.Records[0].s3.bucket.name;
    var srcKey    = event.Records[0].s3.object.key;
    
    // Sanity checks
    if (srcBucket != in_bucket) {
        console.error("Wrong bucket:", in_bucket, srcBucket);
        return;
    }
    
    var typeMatch = srcKey.match(/\.([^.]*)$/);
    if (!typeMatch) {
        console.log('skipping wrong filetype: ' + srcKey);
        return;
    }
    
    var fileType = typeMatch[1];
    if (fileType != "html") {
        console.log('skipping wrong filetype: ' + srcKey);
        return;
    }

    var dstKey = srcKey.slice(0,-5) + ".svg";
    
    async.waterfall([
        //
        // 1. Get file from S3
        //
        function download(next) {
            // Download the image from S3 into a buffer.
            s3.getObject({
                    Bucket: in_bucket,
                    Key: srcKey
                },
                next);
            console.log("GET "+srcKey);
            },

        //
        // 2. Write to a file for exe -- must be in /tmp/
        //
        function write_to_file(response, next) {
            fs.writeFile("/tmp/stdin.html", response.Body, next);
        },  
        //
        // 3. Process file
        //
        function transform(next) {
            var exe = spawn('./phantomjs', ['extract_svg.js', '/tmp/stdin.html']);
            var content_type = "image/svg+xml";
            var data_type = "binary";
            
            var buffers = [];
            exe.stdout.on('data', function(data) {
              buffers.push(new Buffer(data, data_type));
            });
            
            exe.stderr.on('data', function(data) {
                // otherwise it hangs waiting to be read
            });
            
            exe.on('exit', function(code) {
              console.log("exit");
              var allbuffer = Buffer.concat(buffers)
              // filetype
              next(null, content_type, allbuffer);
            });
        },
        
        //
        // Put back on S3 in out_bucket
        //
        function upload(contentType, data, next) {
            // Stream the transformed image to a different S3 bucket.
            s3.putObject({
                    Bucket: out_bucket,
                    Key: dstKey,
                    Body: data,
                    ContentType: contentType
                },
                next);
            }
        ], function (err) {
            if (err) {
                console.error(
                    'Failed: ' + in_bucket + '/' + srcKey + ' ' + out_bucket + '/' + dstKey +
                    ' Error: ' + err
                );
            } else {
                console.log(
                    'Succeeded: ' + in_bucket + '/' + srcKey + ' ' + out_bucket + '/' + dstKey
                );
            }
            context.done();
        }
    );
};
