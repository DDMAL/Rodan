//Default threshold before user input
//Maximum value for greyness
//Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
var widthLim = 750;
var heightLim = 750;
var imageObj;
var defAngle = 0;
var scaleVal = 1;

//Setup
window.onload = function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = initImage;
    
    //Image path (TO BE REPLACED LATER)
    imageObj.src = $("#image-original").attr("src");
    
    //jQuery slider definition for threshold controller
    $(function() {
		$(".knob").knob({
		    'value':defAngle,
			'min':0,
			'max':360,
			'displayPrevious':true,
			'change':function(v, ipt) {
			    rotate(v);
			}
		});
	});
	
	$('#rotate-form').submit(function () {
	    var outAngle = (defAngle > 180) ? (defAngle - 360) : defAngle;
        $('#angle-input').val(outAngle);
    });
};

initImage = function() {
    //Adjust size of canvas to fit image
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    if (imageObj.width > widthLim || imageObj.height > heightLim) {
        var scaleValX = 0;
        var scaleValY = 0;
        scaleValX = widthLim / imageObj.width;
        scaleValY = heightLim / imageObj.height;
        scaleVal = Math.min(scaleValX, scaleValY);
        canvas.width = canvas.width * scaleVal;
        canvas.height = canvas.height * scaleVal;
        imageObj.height *= scaleVal;
        imageObj.width *= scaleVal;
    }
    var dist = Math.ceil(Math.sqrt(Math.pow(imageObj.width, 2) + Math.pow(imageObj.height, 2)));
    canvas.width = dist;
    canvas.height = dist;
    context.scale(scaleVal, scaleVal);
    rotate(0);
}

//Binarizes data, splitting foreground and background at a given brightness level
rotate = function(angle) {
    defAngle = angle;
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width / scaleVal, canvas.height /  scaleVal);
    context.save();
    context.translate(canvas.width / (2 * scaleVal), canvas.height / (2 * scaleVal));
    context.rotate(angle * Math.PI / 180);
    context.translate(-canvas.width / (2 * scaleVal), -canvas.height / (2 * scaleVal));
    var drawX = (canvas.width - imageObj.width) / (2 * scaleVal);
    var drawY = (canvas.height - imageObj.height) / (2 * scaleVal);
    context.drawImage(imageObj, drawX, drawY);
    context.restore();
}