//
// http://docs.aws.amazon.com/AWSJavaScriptSDK/guide/node-examples.html
// http://www.sebastianseilund.com/nodejs-async-in-practice
// To test, remove exports.hander and context.done(), 
// change ./phantomjs to ./mac_phantomjs
// export AWS_ACCESS_KEY_ID='AKIAIHCPZI3MPF5B6DYQ'
// export AWS_SECRET_ACCESS_KEY=''
// var srcBucket = in_bucket;
// var srcKey    = "lh34o.html";
//
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
    
    //------------------------------------------------------------------------------------
    // Sanity checks
    //
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

    var dstKey_svg = srcKey.slice(0,-5) + ".svg";
    var dstKey_png = srcKey.slice(0,-5) + ".png";
    
    async.waterfall([
        //--------------------------------------------------------------------------------
        // 1. Get file from S3
        //
        function download_from_S3(next) {
            s3.getObject({
                Bucket: in_bucket,
                Key: srcKey
            }, next);
            console.log("GET "+srcKey);
        },
        
        //--------------------------------------------------------------------------------
        // 2. Write to a file for exe -- must be in /tmp/
        //
        function write_to_file(response, next) {
            console.log("write to /tmp/");
            fs.writeFile("/tmp/stdin.html", response.Body, next);
        },
        
        //--------------------------------------------------------------------------------
        // 3. Process file, extract SVG and render PNG to /tmp/out.{svg|png}
        //
        function transform(next) {
            console.log("wrote to temp, do exe");
            var exe = spawn('./phantomjs', ['extract_svg_png.js', '/tmp/stdin.html', '/tmp/out']);            
            // Not sure if these two are necessary
            // They are when reading data from stdout.
            // Add a 5ms timeout just in case file has not finished writing
            exe.stdout.on('data', function(data) { console.log(data); });
            exe.stderr.on('data', function(data) { console.error(data); });
            exe.on('exit', next);
        },
        function wait_for_file_write(exe_out, next) {
            setTimeout(next,5);
        },
        
        //--------------------------------------------------------------------------------
        // Dump multiple files to S3 buckets 
        //
        function multi_upload(next) {
            console.log("multi upload", dstKey_svg, dstKey_png);
            async.parallel([
                function(pnext) {
                    var body = fs.createReadStream('/tmp/out.svg');
                    s3.putObject({
                            Bucket: out_bucket,
                            Key: dstKey_svg,
                            Body: body,
                            ContentType: "image/svg+xml"
                        }, pnext);
                },
                function(pnext) {
                    var body = fs.createReadStream('/tmp/out.png');
                    s3.putObject({
                            Bucket: out_bucket,
                            Key: dstKey_png,
                            Body: body,
                            ContentType: "image/png"
                        }, pnext);
                }
            ], next);
        },
        //--------------------------------------------------------------------------------
        // end of waterfall, final callback, check if everything worked
        //
        ], function (err) { 
            console.log("final waterfall callback");
            if (err) {
                console.error('Failed: ' + in_bucket + '/' + srcKey + ' ' + out_bucket + 
                              '/' + dstKey_svg + ' Error: ' + err);
            }
            else {
                console.log('Succeeded: ' + in_bucket + '/' + srcKey + ' ' + out_bucket + 
                            '/' + dstKey_svg);
            }
            context.done();
        }
    );
};
