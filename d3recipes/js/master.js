
String.prototype.startsWith = function(prefix) {
    return this.indexOf(prefix) === 0;
}

String.prototype.endsWith = function(suffix) {
    return this.match(suffix+"$") == suffix;
};


function get_svg_heart(fill, scale, dropshadow) {
    var scale, wh, drop, dropfill;

    if (scale == null) {
        scale = 0.03;
        wh = 20;
    }
    else {
        wh = 7*scale*100;
    }
    
    if (dropshadow !== true) {
        drop = '';
        dropfill = '';
    }
    else {
        var dx = 20 * (scale/0.03);
        var dy = 30 * (scale/0.03);
        var sd = 10 * (scale/0.03);
        drop =  '<defs>' +
            '<filter id="dropshadow" height="130%">' +
            '<feGaussianBlur in="SourceAlpha" stdDeviation="3"/>' +
            '<feOffset dx="30" dy="30" result="offsetblur"/>' +
            '<feComponentTransfer><feFuncA type="linear" slope="0.2"/></feComponentTransfer>' +
            '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/> </feMerge>' +
            '</filter>' +
            '</defs>';
        dropfill = 'filter="url(#dropshadow)"';
    }
    
    var mysvg = '<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" '+
    'version="1.0" width="'+wh+'" height="'+wh+'" class="svgheart">' +
    drop +
    '  <g id="layer1" '+dropfill+' transform="scale('+scale+')">' +
    '    <path id="path2417" style="fill:'+fill+'" d="M 297.29747,550.86823 C 283.52243,535.43191 249.1268,505.33855 220.86277,483.99412 C 137.11867,420.75228 125.72108,411.5999 91.719238,380.29088 C 29.03471,322.57071 2.413622,264.58086 2.5048478,185.95124 C 2.5493594,147.56739 5.1656152,132.77929 15.914734,110.15398 C 34.151433,71.768267 61.014996,43.244667 95.360052,25.799457 C 119.68545,13.443675 131.6827,7.9542046 172.30448,7.7296236 C 214.79777,7.4947896 223.74311,12.449347 248.73919,26.181459 C 279.1637,42.895777 310.47909,78.617167 316.95242,103.99205 L 320.95052,119.66445 L 330.81015,98.079942 C 386.52632,-23.892986 564.40851,-22.06811 626.31244,101.11153 C 645.95011,140.18758 648.10608,223.6247 630.69256,270.6244 C 607.97729,331.93377 565.31255,378.67493 466.68622,450.30098 C 402.0054,497.27462 328.80148,568.34684 323.70555,578.32901 C 317.79007,589.91654 323.42339,580.14491 297.29747,550.86823 z"/>' +
    '  </g>' +
    '</svg>';
    return mysvg;
}

function get_random_id(n, base) {
    if (base > 62) throw "Base must be <= 62";
    var text = "";
    var abet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".substr(0,base);
    
    for( var i=0; i < n; i++ )
        text += abet.charAt(Math.floor(Math.random() * abet.length));

    return text;
}


function get_chart_id() {
    return get_random_id(8, 62);
}


function get_recipe_id(new_recipe_id) {
    if (new_recipe_id !== true) {
        new_recipe_id = false;
    }
    
    if (recipe_id == null || recipe_id == '' || new_recipe_id === true)
        return get_random_id(6, 36);
    else
        return recipe_id;
}
