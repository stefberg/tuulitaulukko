
var canvas;
var context;
var viewMatrix;
var drawAreaWidth;
var drawAreaHeight;
var leftMargin = 20;
var bottomMargin = 20;
var rightMargin = 0;
var topMargin = 0;
var dataMaxX = 100;
var dataMaxY = 20;

function viewX(dataX) 
{
}

function viewY(dataY) 
{
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

function drawGraph()
{
    canvas = document.getElementById("graphCanvas");
    context = canvas.getContext("2d");

    drawAreaWidth = (canvas.width-leftMargin-rightMargin);
    drawAreaHeight = (canvas.height-bottomMargin-topMargin);

    viewMatrix = translateMatrix(0, canvas.height);
    viewMatrix = viewMatrix.multiply(flipYMatrix());
    viewMatrix = viewMatrix.multiply(translateMatrix(leftMargin, bottomMargin));
    viewMatrix = viewMatrix.multiply(scaleMatrix(drawAreaWidth / canvas.width,
                                                 drawAreaHeight / canvas.height));
    drawBox();

    viewMatrix = viewMatrix.multiply(scaleMatrix(drawAreaWidth / dataMaxX,
                                                 drawAreaHeight/ dataMaxY));
//    debugMatrix(viewMatrix);

    moveTo(0, 0);
    lineTo(10, 10);
    lineTo(10, 0);
    lineTo(20, 20);
    lineTo(30, 10);
    stroke();
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
