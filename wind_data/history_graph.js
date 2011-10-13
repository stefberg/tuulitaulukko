
var xmlhttp;
var canvas;
var context;
var windowMatrix;
var dataMatrix;
var viewMatrix; // = dataMatrix x windowMatrix
var drawAreaWidth;
var drawAreaHeight;
var leftMargin = 20;
var bottomMargin = 20;
var rightMargin = 0;
var topMargin = 8;
var dataMaxY = 20;
var dataMaxX = 100;
var dataMinX = 0;
var fetchYear;
var fetchDay;
var fetchStation;
var stationsList;

// check also data today from yesterday 
var stationData;

var data = new Array();

function parseData() 
{
    var sa = stationData.split("\n");
    var l;
    for (l = 0; l < sa.length; l++) {
        var fields = sa[l].split(",");
        if (fields.length > 5) {
            var time = fields[5];
            time = time.split(":");
            var checkHour = parseInt(fields[3]);
            var hour = parseInt(time[0]);
            if (hour > checkHour) {// value from the day before
                hour -= 24;
            }
            var minute = parseInt(time[1]);
            var wind = parseInt(fields[8]);
            var d = new Array();
            d.push(hour*60+minute);
            d.push(wind);
            data.push(d);
        }
        
    }
}

function moveTo(x, y)
{
    var p1 = $V([x, y, 1]);
    p1 = viewMatrix.multiply(p1);
    context.moveTo(p1.e(1), p1.e(2));
}

function lineTo(x, y)
{
    var p1 = $V([x, y, 1]);
    p1 = viewMatrix.multiply(p1);
    context.lineTo(p1.e(1), p1.e(2));
}

function stroke()
{
    context.stroke();
}

function drawBox() 
{
    moveTo(0, 0);
    lineTo(drawAreaWidth, 0);
    lineTo(drawAreaWidth, drawAreaHeight);
    lineTo(0, drawAreaHeight);
    lineTo(0, 0);
    stroke();
}

function drawLabels() 
{
    context.fillStyle    = '#000000';
    var y;
    for (y = 0; y < dataMaxY; y += 6) {
        var p1 = $V([0, y, 1]);
        p1 = viewMatrix.multiply(p1);
        context.fillText(y + "", 2, p1.e(2));
        moveTo(dataMinX, y);
        lineTo(dataMaxX, y);
        stroke();
    }
    var p1 = $V([0, dataMaxY, 1]);
    p1 = viewMatrix.multiply(p1);
    context.fillText(dataMaxY + "", 2, p1.e(2));
}

function translateMatrix(x, y) 
{
    return $M([
                  [1, 0, x],
                  [0, 1, y],
                  [0, 0, 1]
               ]);
}

function scaleMatrix(x, y) 
{
    return $M([
                  [x, 0, 0],
                  [0, y, 0],
                  [0, 0, 1]
               ]);
}

function flipYMatrix()
{
    return $M([
                  [1, 0, 0],
                  [0, -1, 0],
                  [0, 0, 1]
               ]);
}

function fetchData()
{
    xmlhttp.onreadystatechange=function()
        {
            if (xmlhttp.readyState==4/* && xmlhttp.status==200*/)
            {
//                debug(xmlhttp.responseText);
                stationData = xmlhttp.responseText;
                parseAndDrawData();
            }
        }
    xmlhttp.open("GET", fetchStation + "_" + fetchYear + "-" + fetchDay + ".txt", true);
    xmlhttp.send();
    debug("xmlhttp.send");
}

function parseAndDrawData()
{
    parseData();
    
    var i;
    dataMaxX = 0;
    dataMinX = 1000000;
    dataMaxY = 0;

    for (i = 0; i < data.length; i++) {
        if (data[i][0] > dataMaxX) {
            dataMaxX = data[i][0];
        }
        if (data[i][0] < dataMinX) {
            dataMinX = data[i][0];
        }
        if (data[i][1] > dataMaxY) {
            dataMaxY = data[i][1];
        }
    }

    dataMatrix = scaleMatrix(drawAreaWidth / (dataMaxX - dataMinX),
                             drawAreaHeight/ dataMaxY);
    dataMatrix = dataMatrix.multiply(translateMatrix(-dataMinX, 0));

    viewMatrix = windowMatrix.multiply(dataMatrix);
    drawLabels();

    for (i = 0; i < data.length; i++) {
        if (i == 0) {
            moveTo(data[i][0], data[i][1]);
        } else {
            lineTo(data[i][0], data[i][1]);
        }
    }
    stroke();
}

function parseStationsList()
{
  var sa = stationsList.split("\n");
  var yearDay = sa[0].split(",");
  fetchYear = parseInt(yearDay[0]);
  fetchDay  = parseInt(yearDay[1]);
  fetchStation = sa[1];
  fetchData();
}

function fetchStations() 
{
    xmlhttp.onreadystatechange=function()
        {
            if (xmlhttp.readyState==4/* && xmlhttp.status==200*/)
            {
                debug(xmlhttp.responseText);
	      stationsList = xmlhttp.responseText;
	      parseStationsList();
            }
        }
    xmlhttp.open("GET", "stations.txt", true);
    xmlhttp.send();
}

function drawGraph()
{
    canvas = document.getElementById("graphCanvas");
    context = canvas.getContext("2d");

    drawAreaWidth = (canvas.width-leftMargin-rightMargin);
    drawAreaHeight = (canvas.height-bottomMargin-topMargin);

    windowMatrix = translateMatrix(0, canvas.height);
    windowMatrix = windowMatrix.multiply(flipYMatrix());
    windowMatrix = windowMatrix.multiply(translateMatrix(leftMargin, bottomMargin));
    windowMatrix = windowMatrix.multiply(scaleMatrix(drawAreaWidth / canvas.width,
                                                     drawAreaHeight / canvas.height));
    viewMatrix = windowMatrix;
    drawBox();
    
    xmlhttp=new XMLHttpRequest();
    fetchStations();
}

function debugMatrix(m)
{
    debug("vm:<br/>" + m.e(1,1) + " " + m.e(1,2) + " " + m.e(1,3) + "<br/>" + 
          m.e(2,1) + " " + m.e(2,2) + " " + m.e(2,3) + "<br/>" + 
          m.e(3,1) + " " + m.e(3,2) + " " + m.e(3,3));
}

function debugVector(v)
{
    debug("v: " + v.e(1) + " " + v.e(2) + " " + v.e(3));
}

function debug(s) 
{
    document.getElementById('debug').innerHTML = document.getElementById('debug').innerHTML + "<br/>" + s;
}
