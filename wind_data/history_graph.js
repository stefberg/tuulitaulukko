
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
var topMargin = 4;
var dataMaxY = 20;
var dataMinY = 0;
var dataMaxX = 100;
var dataMinX = 0;
var fetchYear;
var fetchDay;
var fetchNumDays = 2;
var fetchStartDay;
var fetchEndDay;
var lastFetchedDay;
var fetchStation;
var firstWeekDay;
var stationsList;
var dataDir = './';

var DF_YDAY = 0;
var DF_MINUTE = 1;
var DF_WIND = 2;
var DF_WIND_MIN = 3;
var DF_WIND_MAX = 4;
var DF_WIND_DIR = 5;
var DF_TEMP = 6;

var drawSetTemp = [DF_TEMP];
var drawSetWind = [DF_WIND_MAX, DF_WIND, DF_WIND_MIN];
var drawSetWindDir = [DF_WIND_DIR];
var drawSet = drawSetWind;

var lineColors = ["rgb(200, 0, 0)", "rgb(0,0,0)", "rgb(190, 190, 0)"];

//var weekDays = ["su", "mo", "tu", "we", "th", "fr", "sa"];
var weekDays = ["su", "ma", "ti", "ke", "to", "pe", "la"];

var httpStatusOK = 200;

function trimLeading0(str) 
{
  var ret = str.replace(/^0+/g, '') ;
  if (ret.length == 0) {
    ret = '0';
  }
  return ret;
}

function trim(str)
{
  return str.replace(/^ +/g, '') ;
}

var WINDMAP = {"pohjois": 0, "etelä": 180, "itä": 90, "länsi": 270, "luoteis": 315, "kaakkois": 135, "lounais": 225, "koillis": 45};

function parseWindDir(str) {
  str = trim(str.toLowerCase());
  if (str.charAt(0) >= '0' && str.charAt(0) <= '9') {
    return parseFloat(str);
  }
  return WINDMAP[str];
}

function nona(s) 
{
    if (s == 'na' || s == 'nan') {
        return '0';
    }
    return s;
}

function parseData(yday, dataStr) 
{
  var sa = dataStr.split("\n");
  var l;
  for (l = 0; l < sa.length; l++) {
    var fields = sa[l].split(",");
      if (sa[l].indexOf("nan") < 0 && fields.length > 5 && fields[5].indexOf(":") > 0 && fields[8] != "nan") {
      if (fields[5].indexOf("T") > 0) {
        // time format is like "2024-07-06T10:00:00" so we leave just the last part to work like the hh:mm format like for other
        fields[5] = fields[5].split("T")[1];
      }
      var time = fields[5].split(":");
      var checkHour = parseInt(fields[3]);
      var hour = parseInt(trimLeading0(time[0]));
      if (hour - checkHour > 20) {// value from the day before
        hour -= 24;
      }
      if (l == 0 && data.length == 0) {
        var year = parseInt(fields[0]);
        var month = parseInt(fields[1]);
        var day = parseInt(fields[2]);
        var hour = parseInt(fields[3]);
        var date = new Date(year, month-1, day, hour, 0, 0, 0);
        firstWeekDay = date.getDay();
      }
      var minute = parseInt(trimLeading0(time[1]));
      var windDir = parseWindDir(nona(fields[6]));
      var windMin = parseFloat(nona(fields[7]));
      var wind = parseFloat(nona(fields[8]));
      var windMax = parseFloat(nona(fields[9]));
      var temp = parseFloat(nona(fields[10]));
      var minuteFromStart = (yday - fetchStartDay)*24*60 + hour*60+minute;
      //      debug(l + " T: " + checkHour + " " + time[0] + " " + time[1] + " " + fields[5] + " " + hour+":"+minute);
      //      debug(l + " M: " + minuteFromStart + " W: " + wind);
      var d = new Array();
      d.push(yday);
      d.push(minuteFromStart);
      d.push(wind);
      d.push(windMin);
      d.push(windMax);
      d.push(windDir);
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

function fillRect(x1, y1, w, h)
{
    var p1 = $V([x1, y1, 1]);
    p1 = viewMatrix.multiply(p1);
    var p2 = $V([x1+w, y1+h, 1]);
    p2 = viewMatrix.multiply(p2);
    context.fillRect(p1.e(1), p1.e(2), p2.e(1)-p1.e(1), p2.e(2)-p1.e(2));
}

var sunset = 21*60;
var sunrise = 6*60;

function nextSunset(minute)
{
  var d = round(minute/(60*24), 0);
  var dayMinute = minute - d*60*24;
  if (dayMinute < sunrise) {
    return minute;
  }
  return sunset + d * 60*24;
}

function nextSunrise(minute)
{
  var d = round(minute/(60*24), 0);
  var dayMinute = minute - d*60*24;
  return sunrise + d * 60*24;
}

function drawBackground()
{
  context.beginPath();
  context.fillStyle = 'rgb(240, 240, 240)';
  var ss = dataMinX+1;
  var sr = dataMinX;
  do {
    ss = nextSunset(ss);
    sr = nextSunrise(ss);
    if (sr < dataMaxX) {
      if (ss > dataMaxX) {
	ss = dataMaxX;
      }
      fillRect(ss, dataMinY, sr-ss, dataMaxY-dataMinY);
    }
    ss = sr + 1;
  } while (sr < dataMaxX);
}

function drawLabels() 
{
    context.beginPath();
    context.fillStyle = '#000000';
    context.strokeStyle = 'rgb(220, 220, 220)';
    var grid1 = 2;
    var grid2 = 6;
    if (dataMaxY - dataMinY> 200) {
      grid1 = 45;
      grid2 = 90;
    }
    var y;
    for (y = dataMinY; y < dataMaxY; y += grid1) {
        var p1 = $V([0, y, 1]);
        p1 = viewMatrix.multiply(p1);
        context.fillText(y + "", 2, p1.e(2));
        moveTo(dataMinX, y);
        lineTo(dataMaxX, y);
        stroke();
    }
    context.beginPath();
    context.strokeStyle = '#000000';
    for (y = dataMinY; y < dataMaxY; y += grid2) {
        var p1 = $V([0, y, 1]);
        p1 = viewMatrix.multiply(p1);
        context.fillText(y + "", 2, p1.e(2));
        moveTo(dataMinX, y);
        lineTo(dataMaxX, y);
        stroke();
    }
    var p1 = $V([0, dataMaxY-dataMinY, 1]);
    p1 = viewMatrix.multiply(p1);
    context.fillText(dataMaxY + "", 2, p1.e(2));

    var gridX = 60*3;
    if ((dataMaxX - dataMinX) / (24*60) > 5) {
      gridX = 60*12;
    }
    var x;
    for (x = dataMinX; x < dataMaxX; x += gridX) {
        var min = x;
        var hour3 = round(min/60/3, 0);
        var p1 = $V([hour3*60*3, 0, 1]);
        p1 = viewMatrix.multiply(p1);
        moveTo(hour3*3*60, dataMinY);
        lineTo(hour3*3*60, dataMaxY);
        stroke();
        while (hour3 >= 24/3) {
          hour3 -= 24/3;
        }
        context.fillText(hour3*3 + "", p1.e(1), canvas.height - 2);    
    }
    var d = firstWeekDay;
    for (x = 0; x < dataMaxX; x += 24*60) {
      var p1 = $V([x+6*60, 0, 1]);
      p1 = viewMatrix.multiply(p1);
      context.fillText(weekDays[d], p1.e(1), 15);
      d++;
      if (d > 6) {
        d = 0;
      }
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
    lastFetchedDay = -1;
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
        lastFetchedDay = day;
		drawGraph();
	      }
	    if (day != fetchEndDay) {
	      fetchData(day+1);
	    }
	  }
	}
    var file = dataDir + fetchStation + "_" + fetchYear + "-" + day + ".txt";
//    debug(file);
    xmlhttp.open("GET", file, true);
    xmlhttp.send();
}

function calcRange()
{
    var i;
    dataMaxX = 0;
    dataMinX = 1000000;
    dataMaxY = -1000000;
    dataMinY = 1000000;
    for (i = 0; i < data.length; i++) {
      var d;
      for (d = 0; d < drawSet.length; d++) {
        var yVal = data[i][drawSet[d]];
        if (yVal > dataMaxY) {
          dataMaxY = yVal;
        }      
        if (yVal < dataMinY) {
          dataMinY = yVal;
        }      
      }
      if (data[i][DF_MINUTE] > dataMaxX) {
        dataMaxX = data[i][DF_MINUTE];
      }
      if (data[i][DF_MINUTE] < dataMinX) {
        dataMinX = data[i][DF_MINUTE];
      }
    }
    if (dataMinY >= 0) {
      dataMinY = 0;
    } else {
      dataMinY = Math.floor(dataMinY-2)
    }
    if (dataMaxY < 0) dataMaxY = 0;
    if (lastFetchedDay < fetchEndDay) {
        var date = new Date();
        dataMaxX = dataMinX + (fetchEndDay - fetchStartDay)*60*24 + date.getHours()*60 + date.getMinutes();
    }
    if (drawSet == drawSetWindDir) {
      dataMaxY = 360;
      dataMinY = 0;
    }
    dataMatrix = scaleMatrix(drawAreaWidth / (dataMaxX - dataMinX),
                             drawAreaHeight/ (dataMaxY - dataMinY));
    dataMatrix = dataMatrix.multiply(translateMatrix(-dataMinX, -dataMinY));

    viewMatrix = windowMatrix.multiply(dataMatrix);
}

function drawData()
{
    var yVal;
    var prevyVal;
    var d;
    for (d = 0; d < drawSet.length; d++) {
      context.beginPath();
      var prevXVal = -1;
      for (i = 0; i < data.length; i++) {
        yVal = data[i][drawSet[d]];
          if (data[i][DF_MINUTE] > prevXVal) {
              if (i == 0) {
		  moveTo(data[i][DF_MINUTE], yVal);
              } else {
		  //	  if (Math.abs(yVal - prevyVal) > 200) {
		  //	    moveTo(data[i][DF_MINUTE], yVal);
		  //	  } else {
		  lineTo(data[i][DF_MINUTE], yVal);
		  //	  }
              }
              prevyVal = yVal;
	      prevXVal = data[i][DF_MINUTE];
	  }
      }
      context.strokeStyle = lineColors[d];
      stroke();
    }
    context.strokeStyle = "black";
}

function drawAverage()
{
    var averageY = 0;
    var d;
    var x = 0;
    var xVal = data[0][DF_MINUTE];
    for (i = 0; i < data.length; i++) {
        var yVal = 0;
        if (drawSet == drawSetWind) {
            yVal = data[i][DF_WIND];
        } else {
            yVal = data[i][drawSet[0]];
        }
        averageY += yVal*(data[i][DF_MINUTE]-xVal);
        x += (data[i][DF_MINUTE]-xVal);
        xVal = data[i][DF_MINUTE];
    }
    averageY /= (x+1);

    context.beginPath();
    moveTo(dataMinX, averageY);
    lineTo(dataMaxX, averageY);
    context.strokeStyle = "rgb(180, 220, 220)";
    stroke();
    
    context.strokeStyle = "black";
}

function parseStationsList(doFirst)
{
  var sa = stationsList.split("\n");
  createStationSelector(sa);
  var yearDay = sa[0].split(",");
  fetchYear = parseInt(yearDay[0]);
  fetchDay  = parseInt(yearDay[1]);
  if (doFirst) {
    if (fetchStation == '') {
      fetchStation = sa[1];
    }
    startFetchData();
  }
}

function fetchStations(doFirst) 
{
    xmlhttp.onreadystatechange=function()
        {
          if (xmlhttp.readyState==4 && xmlhttp.status == httpStatusOK)
          {
            stationsList = xmlhttp.responseText;
            parseStationsList(doFirst);
          }
        }
    xmlhttp.open("GET", dataDir + "stations.txt", true);
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
    calcRange();
    drawBackground();
    drawLabels();
    drawData();
    drawAverage();
}

function initGraph(doFirst)
{
  if (window.location.host == '') {
    httpStatusOK = 0;
  }
    canvas = document.getElementById("graphCanvas");
    context = canvas.getContext("2d");
    xmlhttp=new XMLHttpRequest();
    fetchStation = window.location.hash.replace('#', '');
    fetchNumDays = parseInt(document.getElementById('days').value);
    fetchStations(doFirst);
}

function showStation(s, d)
{
    if (fetchStation != s) {
      fetchStation = s;
      startFetchData();
    }
    if (d != -1) {
      var i;
      if (d == 0) { i = 'm/s'; }
      if (d == 1) { i = 'temp'; }
      if (d == 2) { i = 'dir'; }
      document.getElementById('station_name').innerHTML = s + ' ' + i;
      document.getElementById('days').style.display = "block";
      changeDrawSet(d);
    }
}

function createStationSelector(stations) {
    var div = document.getElementById("stations");
    if (div != null) {
      var select = document.createElement("select");
      select.onchange=function() { showStation(this.value, -1); }

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
  if (d == 2) {
    drawSet = drawSetWindDir;
  }
  drawGraph();
}

function setDataDir(d) 
{
  dataDir = d;
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
