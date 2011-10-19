
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
var fetchNumDays = 1;
var fetchStartDay;
var fetchEndDay;
var fetchStation;
var stationsList;

var DF_YDAY = 0;
var DF_MINUTE = 1;
var DF_WIND = 2;
var DF_WIND_MIN = 3;
var DF_WIND_MAX = 4;
var DF_TEMP = 5;

var drawSetTemp = [DF_TEMP];
var drawSetWind = [DF_WIND_MIN, DF_WIND, DF_WIND_MAX];
var drawSet = drawSetWind;

var lineColors = ["rgb(150, 150, 0)","rgb(0,0,0)","rgb(200, 0, 0)"];

var httpStatusOK = 200;

function trimLeading0(str) 
{
  var ret = str.replace(/^0+/g, '') ;
  if (ret.length == 0) {
    ret = '0';
  }
  return ret;
}

function parseData(yday, dataStr) 
{
    var sa = dataStr.split("\n");
    var l;
    for (l = 0; l < sa.length; l++) {
        var fields = sa[l].split(",");
        if (fields.length > 5) {
   	    var time = fields[5].split(":");
            var checkHour = parseInt(fields[3]);
            var hour = parseInt(trimLeading0(time[0]));
	    if (hour - checkHour > 20) {// value from the day before
	      hour -= 24;
	    }
            var minute = parseInt(trimLeading0(time[1]));
            var windMin = parseFloat(fields[7]);
            var wind = parseFloat(fields[8]);
            var windMax = parseFloat(fields[9]);
            var temp = parseFloat(fields[10]);
	    var minuteFromStart = (yday - fetchStartDay)*24*60 + hour*60+minute;
	    //	    debug(l + " T: " + checkHour + " " + time[0] + " " + time[1] + " " + fields[5] + " " + hour+":"+minute);
	    //	    debug(l + " M: " + minuteFromStart + " W: " + wind);
            var d = new Array();
	    d.push(yday);
            d.push(minuteFromStart);
            d.push(wind);
            d.push(windMin);
            d.push(windMax);
            d.push(temp);
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
    context.beginPath();
    context.strokeStyle = '#000000';
    moveTo(0, 0);
    lineTo(drawAreaWidth, 0);
    lineTo(drawAreaWidth, drawAreaHeight);
    lineTo(0, drawAreaHeight);
    lineTo(0, 0);
    stroke();
}

function drawLabels() 
{
    context.beginPath();
    context.fillStyle = '#000000';
    context.strokeStyle = 'rgb(220, 220, 220)';
    var y;
    for (y = 2; y < dataMaxY; y += 2) {
        var p1 = $V([0, y, 1]);
        p1 = viewMatrix.multiply(p1);
        context.fillText(y + "", 2, p1.e(2));
        moveTo(dataMinX, y);
        lineTo(dataMaxX, y);
        stroke();
    }
    context.beginPath();
    context.strokeStyle = '#000000';
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

    var x;
    for (x = dataMinX; x < dataMaxX; x += 60*3) {
        var min = x;
	var hour3 = round(min/60/3, 0);
        var p1 = $V([hour3*60*3, 0, 1]);
        p1 = viewMatrix.multiply(p1);
        moveTo(hour3*3*60, 0);
        lineTo(hour3*3*60, dataMaxY);
        stroke();    	while (hour3 >= 24/3) {
	  hour3 -= 24/3;
	}
	context.fillText(hour3*3 + "", p1.e(1), canvas.height - 2);    
    }
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

function startFetchData()
{
    fetchStartDay = fetchDay - fetchNumDays + 1;
    fetchEndDay = fetchStartDay + fetchNumDays - 1;
    //    debug("d: " + fetchNumDays + " " + fetchStartDay + " " + fetchEndDay);

    data = new Array();
    fetchData(fetchStartDay);
}

function fetchData(day)
{
//    debug(day);
    
    xmlhttp.onreadystatechange=function()
        {
	  if (xmlhttp.readyState==4) {
	    if (xmlhttp.status == httpStatusOK)
	      {
		//                debug(xmlhttp.responseText);
		parseData(day, xmlhttp.responseText);
		drawGraph();
	      }
	    if (day != fetchEndDay) {
	      fetchData(day+1);
	    }
	  }
	}
    var file = fetchStation + "_" + fetchYear + "-" + day + ".txt";
//    debug(file);
    xmlhttp.open("GET", file, true);
    xmlhttp.send();
}

function drawData()
{
    var i;
    dataMaxX = 0;
    dataMinX = 1000000;
    dataMaxY = 0;

    for (i = 0; i < data.length; i++) {
      var d;
      for (d = 0; d < drawSet.length; d++) {
	var yVal = data[i][drawSet[d]];
        if (yVal > dataMaxY) {
	  dataMaxY = yVal;
        }      
      }
      if (data[i][DF_MINUTE] > dataMaxX) {
	dataMaxX = data[i][DF_MINUTE];
      }
      if (data[i][DF_MINUTE] < dataMinX) {
	dataMinX = data[i][DF_MINUTE];
      }
    }

    dataMatrix = scaleMatrix(drawAreaWidth / (dataMaxX - dataMinX),
                             drawAreaHeight/ dataMaxY);
    dataMatrix = dataMatrix.multiply(translateMatrix(-dataMinX, 0));

    viewMatrix = windowMatrix.multiply(dataMatrix);

    drawLabels();
    var d;
    for (d = 0; d < drawSet.length; d++) {
      context.beginPath();
      for (i = 0; i < data.length; i++) {
        if (i == 0) {
	  moveTo(data[i][DF_MINUTE], data[i][drawSet[d]]);
        } else {
	  lineTo(data[i][DF_MINUTE], data[i][drawSet[d]]);
        }
      }
      context.strokeStyle = lineColors[d];
      stroke();
    }
    context.strokeStyle = "black";
}

function parseStationsList()
{
  var sa = stationsList.split("\n");
  createStationSelector(sa);
  var yearDay = sa[0].split(",");
  fetchYear = parseInt(yearDay[0]);
  fetchDay  = parseInt(yearDay[1]);
  if (fetchStation == '') {
    fetchStation = sa[1];
  }
  startFetchData();
}

function fetchStations() 
{
    xmlhttp.onreadystatechange=function()
        {
            if (xmlhttp.readyState==4 && xmlhttp.status == httpStatusOK)
            {
	      stationsList = xmlhttp.responseText;
	      parseStationsList();
            }
        }
    xmlhttp.open("GET", "stations.txt", true);
    xmlhttp.send();
}

function drawGraph()
{
    context.beginPath();
    context.clearRect(0 , 0 , canvas.width , canvas.height);

    drawAreaWidth = (canvas.width-leftMargin-rightMargin);
    drawAreaHeight = (canvas.height-bottomMargin-topMargin);

    windowMatrix = translateMatrix(0, canvas.height);
    windowMatrix = windowMatrix.multiply(flipYMatrix());
    windowMatrix = windowMatrix.multiply(translateMatrix(leftMargin, bottomMargin));
    windowMatrix = windowMatrix.multiply(scaleMatrix(drawAreaWidth / canvas.width,
                                                     drawAreaHeight / canvas.height));
    viewMatrix = windowMatrix;
    drawBox();
    drawData();
}

function initGraph()
{
  if (window.location.host == '') {
    httpStatusOK = 0;
  }
    canvas = document.getElementById("graphCanvas");
    context = canvas.getContext("2d");
    xmlhttp=new XMLHttpRequest();
    fetchStation = window.location.hash.replace('#', '');
    fetchStations();
}

function showStation(s) 
{
  fetchStation = s;
  startFetchData();
}

function createStationSelector(stations) {
    var div = document.getElementById("stations");
    var select = document.createElement("select");
    select.onchange=function() { showStation(this.value); }

    for (var i = 1; i < stations.length; i++) {
      opt = document.createElement("option");
      opt.value = stations[i];
      opt.appendChild(document.createTextNode(stations[i]));
      if (fetchStation != '' && fetchStation == stations[i]) {
	opt.selected = true;
      }
      select.add(opt, null);
    }
    div.appendChild(select);
}

function changeDays(d) 
{
    fetchNumDays = parseInt(d);
    startFetchData();
}

function changeDrawSet(d)
{
  if (d == 0) {
    drawSet = drawSetWind;
  }
  if (d == 1) {
    drawSet = drawSetTemp;
  }
  drawGraph();
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

function round(v, dec) { // to number of decimals
    v = Math.round(v * Math.pow(10,dec)) / Math.pow(10,dec);
    return v;
}
