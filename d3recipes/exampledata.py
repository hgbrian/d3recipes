# -*- coding: utf-8 -*-
import random, json

states_json = []

##########################################################################################
# >>> [s['id'] for s in j['objects']['states']['geometries']] (len 53)
# [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56, 72, 78] 
# state_ids (51, (50 states, plus DC))
# [1, 2, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56]

us_states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"];
vals = [random.randint(0,100) for _ in range(len(us_states))]

states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['state','val'],
                  'column_types' : ['text','numeric100'],
                  'readonly_cols' : ['readonly', 'editable'],
                  'fixed_row_col' : [1,1],
                 },
'recipe_params' : [['W',640,'number'], ['H', 480, 'number'], 
                   ['reverse colors',0,'checkbox'], ['color', '#ff0000', 'color']],
'sheet_data' : zip(us_states, vals),
'code':'''<style>

.counties {
  fill: none;
}

.states {
  fill: none;
  stroke: #fff;
  stroke-linejoin: round;
}

.q0-9 { fill:rgb(247,251,255); }
.q1-9 { fill:{{color}}; }
.q2-9 { fill:rgb(198,219,239); }
.q3-9 { fill:rgb(158,202,225); }
.q4-9 { fill:rgb(107,174,214); }
.q5-9 { fill:rgb(66,146,198); }
.q6-9 { fill:rgb(33,113,181); }
.q7-9 { fill:rgb(8,81,156); }
.q8-9 { fill:{{color}}; }

</style>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script src="http://d3js.org/queue.v1.min.js"></script>
<script src="http://d3js.org/topojson.v1.min.js"></script>
<script>
var width = parseInt({{W}}),
    height = parseInt({{H}});


var state_ids = {'Alabama': 1, 'Alaska': 2, 'Arizona': 4, 'Arkansas': 5, 'California': 6, 
    'Colorado': 8, 'Connecticut': 9, 'Delaware': 10, 'District of Columbia': 11, 
    'Florida': 12, 'Georgia': 13, 'Hawaii': 15, 'Idaho': 16, 'Illinois': 17, 
    'Indiana': 18, 'Iowa': 19, 'Kansas': 20, 'Kentucky': 21, 'Louisiana': 22, 'Maine': 23, 
    'Maryland': 24, 'Massachusetts': 25, 'Michigan': 26, 'Minnesota': 27, 
    'Mississippi': 28, 'Missouri': 29, 'Montana': 30, 'Nebraska': 31, 'Nevada': 32, 
    'New Hampshire': 33, 'New Jersey': 34, 'New Mexico': 35, 'New York': 36, 
    'North Carolina': 37, 'North Dakota': 38, 'Ohio': 39, 'Oklahoma': 40, 
    'Oregon': 41, 'Pennsylvania': 42, 'Rhode Island': 44, 'South Carolina': 45, 
    'South Dakota': 46, 'Tennessee': 47, 'Texas': 48, 'Utah': 49, 'Vermont': 50, 
    'Virginia': 51, 'Washington': 53, 'West Virginia': 54, 'Wisconsin': 55, 'Wyoming': 56}

var rateById = d3.map();

var quantize = d3.scale.quantize()
    .domain([0, 100])
    .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

var quantize_reversed = d3.scale.quantize()
    .domain([0, 100])
    .range(d3.range(9).map(function(i) { return "q" + (8-i) + "-9"; }));

var projection = d3.geo.albersUsa()
    .scale(width*1.33333)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.selection().append("svg")
    .attr("width", width)
    .attr("height", height);


var defs = svg.append("defs");
// create filter with id #drop-shadow
// height=130% so that the shadow is not clipped
var filter = defs.append("filter")
    .attr("id", "drop-shadow")
    .attr("height", "130%");

// SourceAlpha refers to opacity of graphic that this filter will be applied to
// convolve that with a Gaussian with standard deviation 3 and store result
// in blur
filter.append("feGaussianBlur")
    .attr("in", "SourceAlpha")
    .attr("stdDeviation", 5)
    .attr("result", "blur");

// translate output of Gaussian blur to the right and downwards with 2px
// store result in offsetBlur
filter.append("feOffset")
    .attr("in", "blur")
    .attr("dx", 5)
    .attr("dy", 10)
    .attr("result", "offsetBlur");

// overlay original SourceGraphic over translated blurred opacity by using
// feMerge filter. Order of specifying inputs is important!
var feMerge = filter.append("feMerge");

feMerge.append("feMergeNode")
    .attr("in", "offsetBlur")
feMerge.append("feMergeNode")
    .attr("in", "states");


queue()
    .defer(d3.json, "https://s3.amazonaws.com/d3recipes/us.json")
    .await(ready);

function ready(error, us) {
    var Gdata = {{data}};
    for (var i=0; i<Gdata.length; i++) {
      rateById.set(parseInt(state_ids[Gdata[i][0]]), Gdata[i][1]);
    }
  
  if ({{reverse colors}}) {
    quantize = quantize_reversed;
  }
  
  
  svg.append("g")
      .attr("class", "states-shadow")
      .style("filter", "url(#drop-shadow)")
    .selectAll("path")
      .data(topojson.feature(us, us.objects.states).features)
    .enter().append("path")
      .attr("d", path);
  
  svg.append("g")
      .attr("class", "states")
    .selectAll("path")
      .data(topojson.feature(us, us.objects.states).features)
    .enter().append("path")
      .attr("class", function(d) { return quantize(rateById.get(d.id)); })
      .attr("d", path);

}

d3.select(self.frameElement).style("height", height + "px");
</script>
'''
}))


states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['state','val'],
                  'column_types' : ['text','numeric100'],
                  'readonly_cols' : ['readonly', 'editable'],
                  'fixed_row_col' : [1,1],
                 },
'recipe_params' : [['W',640,'number'], ['H', 480, 'number'], 
                   ['reverse colors',0,'checkbox'], ['color', '#ff0000', 'color']],
'sheet_data' : zip(us_states, vals),
'code':'''<style>

.counties {
  fill: none;
}

.states {
  fill: none;
  stroke: #fff;
  stroke-linejoin: round;
}

.q0-9 { fill:rgb(247,251,255); }
.q1-9 { fill:{{color}}; }
.q2-9 { fill:rgb(198,219,239); }
.q3-9 { fill:rgb(158,202,225); }
.q4-9 { fill:rgb(107,174,214); }
.q5-9 { fill:rgb(66,146,198); }
.q6-9 { fill:rgb(33,113,181); }
.q7-9 { fill:rgb(8,81,156); }
.q8-9 { fill:{{color}}; }

</style>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script src="http://d3js.org/queue.v1.min.js"></script>
<script src="http://d3js.org/topojson.v1.min.js"></script>
<script>
var width = parseInt({{W}}),
    height = parseInt({{H}});


var state_ids = {'Alabama': 1, 'Alaska': 2, 'Arizona': 4, 'Arkansas': 5, 'California': 6, 
    'Colorado': 8, 'Connecticut': 9, 'Delaware': 10, 'District of Columbia': 11, 
    'Florida': 12, 'Georgia': 13, 'Hawaii': 15, 'Idaho': 16, 'Illinois': 17, 
    'Indiana': 18, 'Iowa': 19, 'Kansas': 20, 'Kentucky': 21, 'Louisiana': 22, 'Maine': 23, 
    'Maryland': 24, 'Massachusetts': 25, 'Michigan': 26, 'Minnesota': 27, 
    'Mississippi': 28, 'Missouri': 29, 'Montana': 30, 'Nebraska': 31, 'Nevada': 32, 
    'New Hampshire': 33, 'New Jersey': 34, 'New Mexico': 35, 'New York': 36, 
    'North Carolina': 37, 'North Dakota': 38, 'Ohio': 39, 'Oklahoma': 40, 
    'Oregon': 41, 'Pennsylvania': 42, 'Rhode Island': 44, 'South Carolina': 45, 
    'South Dakota': 46, 'Tennessee': 47, 'Texas': 48, 'Utah': 49, 'Vermont': 50, 
    'Virginia': 51, 'Washington': 53, 'West Virginia': 54, 'Wisconsin': 55, 'Wyoming': 56}

var rateById = d3.map();

var quantize = d3.scale.quantize()
    .domain([0, 100])
    .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

var quantize_reversed = d3.scale.quantize()
    .domain([0, 100])
    .range(d3.range(9).map(function(i) { return "q" + (8-i) + "-9"; }));

var projection = d3.geo.albersUsa()
    .scale(width*1.33333)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.selection().append("svg")
    .attr("width", width)
    .attr("height", height);


queue()
    .defer(d3.json, "https://s3.amazonaws.com/d3recipes/us.json")
    .await(ready);

function ready(error, us) {
    var Gdata = {{data}};
    for (var i=0; i<Gdata.length; i++) {
      rateById.set(parseInt(state_ids[Gdata[i][0]]), Gdata[i][1]);
    }
  
  if ({{reverse colors}}) {
    quantize = quantize_reversed;
  }
  
  svg.append("g")
      .attr("class", "states")
    .selectAll("path")
      .data(topojson.feature(us, us.objects.states).features)
    .enter().append("path")
      .attr("class", function(d) { return quantize(rateById.get(d.id)); })
      .attr("d", path);

}

d3.select(self.frameElement).style("height", height + "px");
</script>
'''
}))


















##########################################################################################
states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['values'],
                  'column_types' : ['numeric'],
                  'readonly_cols' : ['editable'],
                  'fixed_row_col' : [0,1],
                 },
'recipe_params' : [['W',640,'number'], 
                   ['H', 480, 'number'], 
                   ['color', '#4682B4', 'color'],
                   ['min x', 0, 'number'],
                   ['max x', 0, 'number'],
                   ['num bins', 20, 'number']],
'sheet_data' : [[random.randint(0,50)] for _ in range(100)],
'code':'''<!DOCTYPE html>
<meta charset="utf-8">
<style>

body {
  font: 10px sans-serif;
}

.bar rect {
  fill: {{color}};
  shape-rendering: crispEdges;
}

.bar text {
  fill: #fff;
}

.axis path, .axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

</style>

<body>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script>

//----------------------------------------------------------------------------------------

var values = {{data}};
values = values.map(function(v) { return v[0] });

var num_bins = {{num bins}};
var min_x = d3.min(values),
    max_x = d3.max(values);
if ({{min x}} < {{max x}}) {
    min_x = {{min x}};
    max_x = {{max x}};
}
var W = {{W}};
var H = {{H}};
var M = 30;

//----------------------------------------------------------------------------------------

// A formatter for counts.
var formatCount = d3.format(",.0f");

var margin = {top: M, right: M, bottom: M, left: M},
    width = W - margin.left - margin.right,
    height = H - margin.top - margin.bottom;

var x = d3.scale.linear()
    .domain([min_x, max_x])
    .range([0, width])
    .nice(); // http://chimera.labs.oreilly.com/books/1230000000345/ch07.html#_other_methods

console.log(x.domain());

// Generate a histogram using uniformly-spaced bins.
var data = d3.layout.histogram()
    .bins(x.ticks(num_bins))
    (values);

var y = d3.scale.linear()
    .domain([0, d3.max(data, function(d) { return d.y; })]).nice()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var bar = svg.selectAll(".bar")
    .data(data)
  .enter().append("g")
    .attr("class", "bar")
    .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });


bar.append("rect")
    .attr("x", 1)
    .attr("width", x(data[0].dx+x.domain()[0])-1)
    .attr("height", function(d) { return height - y(d.y); });


bar.append("text")
    .attr("dy", ".75em")
    .attr("y", 6)
    .attr("x", x(data[0].dx+x.domain()[0]) / 2) // middle of the bar
    .attr("text-anchor", "middle")
    .text(function(d) { return formatCount(d.y); });

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

</script>'''}))









##########################################################################################
states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['time', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'], 
                  'column_types' : ['string', 'numeric','numeric','numeric','numeric','numeric','numeric','numeric'],
                  'readonly_cols' : ['readonly','editable','editable','editable','editable','editable','editable','editable'],
                  'fixed_row_col' : [1,1],
                 },
'recipe_params' : [['W',960,'number'], 
                   ['H', 430, 'number']],
'sheet_data' : [
        ['1a', 16, 9, 70, 4, 0, 47, 22], 
        ['2a', 20, 25, 55, 0, 2, 38, 11], 
        ['3a', 0, 49, 51, 12, 4, 65, 12], 
        ['4a', 0, 57, 55, 6, 11, 60, 9], 
        ['5a', 0, 61, 17, 2, 28, 50, 0], 
        ['6a', 2, 37, 20, 0, 49, 65, 13], 
        ['7a', 0, 66, 9, 0, 51, 50, 5], 
        ['8a', 9, 70, 4, 0, 47, 22, 8], 
        ['9a', 25, 55, 0, 2, 38, 11, 8], 
        ['10a', 49, 51, 12, 4, 65, 12, 0], 
        ['11a', 57, 55, 6, 11, 60, 9, 0], 
        ['12a', 61, 17, 2, 28, 50, 0, 2], 
        ['1p', 37, 20, 0, 49, 65, 13, 5], 
        ['2p', 66, 9, 0, 51, 50, 5, 12], 
        ['3p', 70, 4, 0, 47, 22, 8, 34], 
        ['4p', 55, 0, 2, 38, 11, 8, 43], 
        ['5p', 51, 12, 4, 65, 12, 0, 54], 
        ['6p', 55, 6, 11, 60, 9, 0, 44], 
        ['7p', 17, 2, 28, 50, 0, 2, 40], 
        ['8p', 20, 0, 49, 65, 13, 5, 48], 
        ['9p', 9, 0, 51, 50, 5, 12, 54], 
        ['10p', 4, 0, 47, 22, 8, 34, 59], 
        ['11p', 0, 2, 38, 11, 8, 43, 60], 
        ['12p', 12, 4, 65, 12, 0, 54, 51]
      ],
'code':'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      rect.bordered {
        stroke: #E6E6E6;
        stroke-width:2px;   
      }

      text.mono {
        font-size: 9pt;
        font-family: Consolas, courier;
        fill: #aaa;
      }

      text.axis-workweek {
        fill: #000;
      }

      text.axis-worktime {
        fill: #000;
      }
    </style>
    <script src="http://d3js.org/d3.v3.js"></script>
  </head>
  <body>
    <div id="chart"></div>

    <script type="text/javascript">
      var Gdata = {{data}};
      var data = [];
      var ix = 0;
      for (var i=0; i<Gdata.length; i++) {
        for (var j=1; j<Gdata[i].length; j++) {
            data[ix] = {day:j, hour:i+1, value:Gdata[i][j]};
            ix += 1;
        }
      }
            
      var margin = { top: 50, right: 0, bottom: 100, left: 30 },
          width = 960 - margin.left - margin.right,
          height = 430 - margin.top - margin.bottom,
          gridSize = Math.floor(width / 24),
          legendElementWidth = gridSize*2,
          buckets = 9,
          colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
          days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
          times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];

    
      var colorScale = d3.scale.quantile()
          .domain([0, buckets - 1, d3.max(data, function (d) { return d.value; })])
          .range(colors);

      var svg = d3.select("#chart").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      var dayLabels = svg.selectAll(".dayLabel")
          .data(days)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", 0)
            .attr("y", function (d, i) { return i * gridSize; })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"); });

      var timeLabels = svg.selectAll(".timeLabel")
          .data(times)
          .enter().append("text")
            .text(function(d) { return d; })
            .attr("x", function(d, i) { return i * gridSize; })
            .attr("y", 0)
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + gridSize / 2 + ", -6)")
            .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

      var heatMap = svg.selectAll(".hour")
          .data(data)
          .enter().append("rect")
          .attr("x", function(d) { return (d.hour - 1) * gridSize; })
          .attr("y", function(d) { return (d.day - 1) * gridSize; })
          .attr("rx", 4)
          .attr("ry", 4)
          .attr("class", "hour bordered")
          .attr("width", gridSize)
          .attr("height", gridSize)
          .style("fill", colors[0]);
          
      heatMap.style("fill", function(d) { return colorScale(d.value); });

      heatMap.append("title").text(function(d) { return d.value; });
          
      var legend = svg.selectAll(".legend")
          .data([0].concat(colorScale.quantiles()), function(d) { return d; })
          .enter().append("g")
          .attr("class", "legend");

      legend.append("rect")
        .attr("x", function(d, i) { return legendElementWidth * i; })
        .attr("y", height)
        .attr("width", legendElementWidth)
        .attr("height", gridSize / 2)
        .style("fill", function(d, i) { return colors[i]; });

      legend.append("text")
        .attr("class", "mono")
        .text(function(d) { return "≥ " + Math.round(d); })
        .attr("x", function(d, i) { return legendElementWidth * i; })
        .attr("y", height + gridSize);
    </script>
  </body>
</html>'''}))






##########################################################################################
states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['age', 'population'],
                  'column_types' : ['string', 'numeric'],
                  'readonly_cols' : ['editable','editable'],
                  'fixed_row_col' : [0,1],
                 },
'recipe_params' : [['W',960,'number'], 
                   ['H', 430, 'number']],
'sheet_data' : [
        ["5",2704659],
        ["5-13",4499890],
        ["14-17",2159981],
        ["18-24",3853788],
        ["25-44",14106543],
        ["45-64",8819342],
        ["≥65",612463]
      ],
'code':'''<!DOCTYPE html>
<meta charset="utf-8">
<style>

body {
  font: 10px sans-serif;
}

.arc path {
  stroke: #fff;
}

</style>
<body>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script>

var width = {{W}},
    height = {{H}},
    radius = Math.min(width, height) / 2;

var color = d3.scale.ordinal()
    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

var arc = d3.svg.arc()
    .outerRadius(radius - 10)
    .innerRadius(0);

var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.population; });

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  var Gdata = {{data}};
  var data = [];
  for (var i=0; i<Gdata.length; i++) {
    data[i] = {"age":Gdata[i][0], "population":Gdata[i][1]};
  }
  console.log(data);


  data.forEach(function(d) {
    d.population = +d.population;
  });

  var g = svg.selectAll(".arc")
      .data(pie(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", arc)
      .style("fill", function(d) { return color(d.data.age); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
      .attr("dy", ".35em")
      .style("text-anchor", "middle")
      .text(function(d) { return d.data.age; });


</script>



'''}))



##########################################################################################
states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['date', 'close'],
                  'column_types' : ['string', 'numeric'],
                  'readonly_cols' : ['editable','editable'],
                  'fixed_row_col' : [0,1],
                 },
'recipe_params' : [['W',1000,'number'], 
                   ['H', 400, 'number']],
'sheet_data' : [
    ['13-Apr-12', '605.23'], ['26-Mar-12', '606.98'], ['7-Mar-12', '530.69'], ['16-Feb-12', '502.21'], ['30-Jan-12', '453.01'], ['10-Jan-12', '423.24'], ['20-Dec-11', '395.95'], ['1-Dec-11', '387.93'], ['11-Nov-11', '384.62'], ['25-Oct-11', '397.77'], ['6-Oct-11', '377.37'], ['19-Sep-11', '411.63'], ['30-Aug-11', '389.99'], ['11-Aug-11', '373.70'], ['25-Jul-11', '398.50'], ['6-Jul-11', '351.76'], ['16-Jun-11', '325.16'], ['27-May-11', '337.41'], ['10-May-11', '349.45'], ['20-Apr-11', '342.41'], ['1-Apr-11', '344.56'], ['15-Mar-11', '345.43'], ['24-Feb-11', '342.88'], ['4-Feb-11', '346.50'], ['18-Jan-11', '340.65'], ['29-Dec-10', '325.29'], ['9-Dec-10', '319.76'], ['19-Nov-10', '306.73'], ['2-Nov-10', '309.36'], ['14-Oct-10', '302.31'], ['27-Sep-10', '291.16'], ['8-Sep-10', '262.92'], ['20-Aug-10', '249.64'], ['3-Aug-10', '261.93'], ['15-Jul-10', '251.45'], ['28-Jun-10', '268.30'], ['9-Jun-10', '243.20'], ['21-May-10', '242.32'], ['4-May-10', '258.68'], ['15-Apr-10', '248.92'], ['29-Mar-10', '232.39'], ['10-Mar-10', '224.84'], ['19-Feb-10', '201.67'], ['2-Feb-10', '195.86'], ['14-Jan-10', '209.43'], ['28-Dec-09', '211.61'], ['9-Dec-09', '197.80'], ['20-Nov-09', '199.92'], ['3-Nov-09', '188.75'], ['15-Oct-09', '190.56'], ['28-Sep-09', '186.15'], ['9-Sep-09', '171.14'], ['20-Aug-09', '166.33'], ['31-Jul-09', '163.39'], ['14-Jul-09', '142.27'], ['25-Jun-09', '139.86'], ['8-Jun-09', '143.85'], ['19-May-09', '127.45'], ['30-Apr-09', '125.83'], ['13-Apr-09', '120.22'], ['25-Mar-09', '106.49'], ['6-Mar-09', '85.30'], ['17-Feb-09', '94.53'], ['28-Jan-09', '94.20'], ['8-Jan-09', '92.70'], ['22-Dec-08', '85.74'], ['3-Dec-08', '95.90'], ['14-Nov-08', '90.24'], ['28-Oct-08', '99.91'], ['9-Oct-08', '88.74'], ['22-Sep-08', '131.05'], ['3-Sep-08', '166.96'], ['14-Aug-08', '179.32'], ['28-Jul-08', '154.40'], ['9-Jul-08', '174.25'], ['19-Jun-08', '180.90'], ['2-Jun-08', '186.10'], ['13-May-08', '189.96'], ['24-Apr-08', '168.94'], ['7-Apr-08', '155.89'], ['18-Mar-08', '132.82'], ['28-Feb-08', '129.91'], ['8-Feb-08', '125.48'], ['22-Jan-08', '155.64'], ['2-Jan-08', '194.84'], ['12-Dec-07', '190.86'], ['23-Nov-07', '171.54'], ['5-Nov-07', '186.18'], ['17-Oct-07', '172.75'], ['28-Sep-07', '153.47'], ['11-Sep-07', '135.49'], ['22-Aug-07', '132.51'], ['3-Aug-07', '131.85'], ['17-Jul-07', '138.91'], ['27-Jun-07', '121.89'], ['8-Jun-07', '124.49'], ['21-May-07', '111.98'], ['2-May-07', '100.39']
    ],
'code':'''
<!DOCTYPE html>
<meta charset="utf-8">
<style>

body {
  font: 10px sans-serif;
}

.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.x.axis path {
  display: none;
}

.line {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
}

</style>
<body>
<script src="http://d3js.org/d3.v3.js"></script>
<script>

var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = {{W}} - margin.left - margin.right,
    height = {{H}} - margin.top - margin.bottom;

var parseDate = d3.time.format("%d-%b-%y").parse;

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.close); });

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var Gdata = {{data}};

var data = [];
for (var i=0; i<Gdata.length; i++) {
    data[i] = {"date":parseDate(Gdata[i][0]), "close":+(Gdata[i][1])};
}

  x.domain(d3.extent(data, function(d) { return d.date; }));
  y.domain(d3.extent(data, function(d) { return d.close; }));

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Price ($)");

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);
//});

</script>


'''}))


##########################################################################################


states_json.append(json.dumps({
'sheet_params' : {'column_headers' : ['A', 'B', 'C', 'D'],
                  'column_types' : ['numeric', 'numeric', 'numeric', 'numeric'],
                  'readonly_cols' : ['editable','editable','editable','editable'],
                  'fixed_row_col' : [0,0],
                 },
'recipe_params' : [['W', 100,'number'], 
                   ['H', 400, 'number'],
                   ['color', "#ff0000", 'color']
                   ],
'sheet_data' : [
             [4.0663933509933633, -0.6193206868184526, 1.8338621180744081, 1.9286594263359274],
             [4.263933509933633, 0.6193206868184526, 1.8338621180744081, 1.9286594263359274],
             [4.363933509933633, 0.3193206868184526, 1.8338621180744081, 2.9286594263359274],
             [4.463933509933633, 0.4193206868184526, 1.5338621180744081, 2.3286594263359274],
             [4.263933509933633, 0.5193206868184526, 2.6338621180744081, 2.4286594263359274],
             [4.163933509933633, -0.4193206868184526, 2.3338621180744081, 2.2286594263359274],
             [4.663933509933633, 0.6193206868184526, 2.8338621180744081, 1.9286594263359274]
    ],
'code':'''<!DOCTYPE html>
<html lang="en"><head>
<title>Violin plot example</title>
<meta charset="utf-8">
<script type="text/javascript" language="javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script type="text/javascript" language="javascript" src="http://d3js.org/d3.v3.min.js"></script>        	

<style>
body {
  font: 10px sans-serif;
}

.area{
  shape-rendering: geometricPrecision;
  fill: {{color}} !important;
}
.boxplot{
  shape-rendering: crispEdges;
  fill: none;
  stroke: black;
  stroke-width: 1px;
}
.boxplot.fill{
  fill: black;
}
.boxplot.mean, .boxplot.median{
  fill: white;
  stroke: white;
}
.boxplot.mean{
  shape-rendering: geometricPrecision;
}
.violin{
  shape-rendering: geometricPrecision;
  fill: none !important;
  stroke: #777;
  stroke-width: 1px;
}

.axis path, .axis line {
  fill: none;
  stroke: #000;
  stroke-width: 1px;
  color-rendering: optimizeQuality !important;
  shape-rendering: crispEdges !important;
  text-rendering: geometricPrecision !important; 

}
</style>

    </head>
<body>
<div id="svgElement1"></div>
<div id="svgElement2"></div>    
</body>


<script>

var Gresults = {{data}};

var results = Gresults[0].map(function(col, i) { 
  return Gresults.map(function(row) { 
    return row[i] 
  })
});


var margin={top:10, bottom:30, left:30, right:10};
var height={{H}};
var boxWidth={{W}};
var width=boxWidth * results.length + 100;
var boxSpacing=10;
var violinColor = "{{color}}";


//-----------------------
// Work out correct range
//
var max_result = Number.NEGATIVE_INFINITY;
var min_result = Number.POSITIVE_INFINITY;
function getMaxOfArray(numArray) {
  return Math.max.apply(null, numArray);
}
var max_domain;
for (var i=0; i<results.length; i++) {
    console.log(results[i]);    
    console.log(getMaxOfArray(results[i]));
    max_result = Math.max(getMaxOfArray(results[i]), max_result);
    min_result = Math.min(getMaxOfArray(results[i]), min_result);
}
console.log(min_result, max_result);

if (-min_result > max_result) {
    max_domain = -min_result;
}
else {
    max_domain = max_result;
}

var domain=[-Math.ceil(max_domain), Math.ceil(max_domain)];


function addViolin(svg, results, height, width, domain, imposeMax, violinColor){
    var data = d3.layout.histogram()
                    .bins(resolution)
                    .frequency(0)
                    (results);

    var y = d3.scale.linear()
                .range([width/2, 0])
                .domain([0, Math.max(imposeMax, d3.max(data, function(d) { return d.y; }))]);

    var x = d3.scale.linear()
                .range([height, 0])
                .domain(domain)
                .nice();


    var area = d3.svg.area()
        .interpolate(interpolation)
        .x(function(d) {
               if(interpolation=="step-before")
                    return x(d.x+d.dx/2)
               return x(d.x);
            })
        .y0(width/2)
        .y1(function(d) { return y(d.y); });

    var line=d3.svg.line()
        .interpolate(interpolation)
        .x(function(d) {
               if(interpolation=="step-before")
                    return x(d.x+d.dx/2)
               return x(d.x);
            })
        .y(function(d) { return y(d.y); });

    var gPlus=svg.append("g")
    var gMinus=svg.append("g")

    gPlus.append("path")
      .datum(data)
      .attr("class", "area")
      .attr("d", area)
      .style("fill", violinColor);

    gPlus.append("path")
      .datum(data)
      .attr("class", "violin")
      .attr("d", line)
      .style("stroke", violinColor);

    gMinus.append("path")
      .datum(data)
      .attr("class", "area")
      .attr("d", area)
      .style("fill", violinColor);

    gMinus.append("path")
      .datum(data)
      .attr("class", "violin")
      .attr("d", line)
      .style("stroke", violinColor);

    var x=width;

    gPlus.attr("transform", "rotate(90,0,0)  translate(0,-"+width+")");//translate(0,-200)");
    gMinus.attr("transform", "rotate(90,0,0) scale(1,-1)");
}



function addBoxPlot(svg, results, height, width, domain, boxPlotWidth, boxColor, boxInsideColor){
    var y = d3.scale.linear()
                .range([height, 0])
                .domain(domain);

    var x = d3.scale.linear()
                .range([0, width])

    var left=0.5-boxPlotWidth/2;
    var right=0.5+boxPlotWidth/2;

    var probs=[0.05,0.25,0.5,0.75,0.95];
    for(var i=0; i<probs.length; i++){
        probs[i]=y(d3.quantile(results, probs[i]))
    }

    svg.append("rect")
        .attr("class", "boxplot fill")
        .attr("x", x(left))
        .attr("width", x(right)-x(left))
        .attr("y", probs[3])
        .attr("height", -probs[3]+probs[1])
        .style("fill", boxColor);

    var iS=[0,2,4];
    var iSclass=["","median",""];
    var iSColor=[boxColor, boxInsideColor, boxColor]
    for(var i=0; i<iS.length; i++){
        svg.append("line")
            .attr("class", "boxplot "+iSclass[i])
            .attr("x1", x(left))
            .attr("x2", x(right))
            .attr("y1", probs[iS[i]])
            .attr("y2", probs[iS[i]])
            .style("fill", iSColor[i])
            .style("stroke", iSColor[i]);
    }

    var iS=[[0,1],[3,4]];
    for(var i=0; i<iS.length; i++){
        svg.append("line")
            .attr("class", "boxplot")
            .attr("x1", x(0.5))
            .attr("x2", x(0.5))
            .attr("y1", probs[iS[i][0]])
            .attr("y2", probs[iS[i][1]])
            .style("stroke", boxColor);
    }

    svg.append("rect")
        .attr("class", "boxplot")
        .attr("x", x(left))
        .attr("width", x(right)-x(left))
        .attr("y", probs[3])
        .attr("height", -probs[3]+probs[1])
        .style("stroke", boxColor);

    svg.append("circle")
        .attr("class", "boxplot mean")
        .attr("cx", x(0.5))
        .attr("cy", y(d3.mean(results)))
        .attr("r", x(boxPlotWidth/5))
        .style("fill", boxInsideColor)
        .style("stroke", 'None');

    svg.append("circle")
        .attr("class", "boxplot mean")
        .attr("cx", x(0.5))
        .attr("cy", y(d3.mean(results)))
        .attr("r", x(boxPlotWidth/10))
        .style("fill", boxColor)
        .style("stroke", 'None');
}

var resolution=10;
var d3ObjId="svgElement1";
var interpolation='step-before';

var y = d3.scale.linear()
            .range([height-margin.bottom, margin.top])
            .domain(domain);

var yAxis = d3.svg.axis()
                .scale(y)
                .ticks(5)
                .orient("left")
                .tickSize(5,0,5);


var d3ObjId="svgElement2";
var interpolation='basis';

var svg = d3.select("#"+d3ObjId)
            .append("svg")
                .attr("width", width)
                .attr("height", height);

svg.append("line")
    .attr("class", "boxplot")
    .attr("x1", margin.left)
    .attr("x2", width-margin.right)
    .attr("y1", y(0))
    .attr("y2", y(0));

for(var i=0; i<results.length; i++){
    results[i]=results[i].sort(d3.ascending)
    var g=svg.append("g").attr("transform", "translate("+(i*(boxWidth+boxSpacing)+margin.left)+",0)");
    addViolin(g, results[i], height, boxWidth, domain, 0.25, violinColor);
    addBoxPlot(g, results[i], height, boxWidth, domain, .15, "black", "white");
}

svg.append("g")
    .attr('class', 'axis')
    .attr("transform", "translate("+margin.left+",0)")
    .call(yAxis);

</script>
</html>'''}))









states_json = [states_json[-1]]
