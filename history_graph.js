
function drawGraph()
{
  var canvas = document.getElementById("graphCanvas");
  var context = canvas.getContext("2d");

  context.moveTo(0, 0);
  context.lineTo(canvas.width, 0);
  context.lineTo(canvas.width, canvas.height);
  context.lineTo(0, canvas.height);
  context.lineTo(0, 0);
  context.stroke();

}
