var imageObj;
var BLACK = 0;
var WHITE = 255;
var rScale = 0.2989;
var gScale = 0.5870;
var bScale = 0.1140;
var defSize = 0;

function Point(x, y) {
    this.x = x;
    this.y = y;
}

function IData(data) {
    this.data = data;
    this.getPoint = function(x, y) {
        var convX = x * 4;
        var convY = y * imageObj.width * 4;
        return this.data[convX + convY];
    };
    this.setPoint = function(x, y, val) {
        var convX = x * 4;
        var convY = y * imageObj.width * 4;
        this.data[convX + convY] = val;
        this.data[convX + convY + 1] = val;
        this.data[convX + convY + 2] = val;
    };
    this.isBlack = function(x, y) {
        return this.getPoint(x, y) === BLACK;
    };
}

//Setup
window.onload = function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = initImage;
    
    //Image path (TO BE REPLACED LATER)
    imageObj.src = $("#image-original").attr("src");
    
    //jQuery slider definition for threshold controller
    $("#slider").slider({
                        animate: true,
                        min: 0,
                        max: 100,
                        orientation: "horizontal",
                        step: 1,
                        value: 0,
                        range: false,
                        change: function(event, ui) {despeckle(ui.value)},
                        });
                        
    $('#despeckle-form').submit(function () {
        $('#size-input').val(defSize * defSize);
    });
};

initImage = function() {
    //Adjust size of canvas to fit image
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    canvas.width = imageObj.width;
    canvas.height = imageObj.height;
    binarize(100);
};

despeckle = function(size) {
    defSize = size;
    var cSize = size;
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    binarize(100);
    if (cSize > 0) {
        var imageDataO = context.getImageData(0, 0, canvas.width, canvas.height);
        var dataO = new IData(imageDataO.data);
        
        dataT = new Array(imageObj.width);
        for (var i = 0; i < imageObj.width; i++) {
            dataT[i] = new Array(imageObj.height);
            for (var j = 0; j < dataT[i].length; j++) {
                dataT[i][j] = 0;
            }
        }
        
        var pixelQueue = [];
        for (var y = 0; y < imageObj.height; ++y) {
            for (var x = 0; x < imageObj.width; ++x) {
                if (dataT[x][y] == 0 && dataO.isBlack(x, y)) {
                    pixelQueue = new Array();
                    pixelQueue.push(new Point(x, y));
                    var bail = false;
                    dataT[x][y] = 1;
                    for (var i = 0; (i < pixelQueue.length) && (pixelQueue.length < cSize); ++i) {
                        var center = pixelQueue[i];
                        for (var y2 = ((center.y > 0) ? center.y - 1 : 0); (y2 < Math.min(center.y + 2, imageObj.height)); ++y2) {
                            for (var x2 = ((center.x > 0) ? center.x - 1 : 0); (x2 < Math.min(center.x + 2, imageObj.width)); ++x2) {
                                if (dataT[x2][y2] == 0 && dataO.isBlack(x2, y2)) {
                                    dataT[x2][y2] = 1;
                                    pixelQueue.push(new Point(x2, y2));
                                } else if (dataT[x2][y2] == 2) {
                                    bail = true;
                                    break;
                                }
                            }
                            if (bail)
                                break;
                        }
                        if (bail)
                            break;
                    }
                    if ((!bail) && (pixelQueue.length < cSize)) {
                        //console.log(pixelQueue.getLength(), cSize);
                        while(pixelQueue.length > 0) {
                            var pointO = pixelQueue.pop();
                            dataO.setPoint(pointO.x, pointO.y, WHITE);
                        }
                    } else {
                        while (pixelQueue.length > 0) {
                            var pointT = pixelQueue.pop();
                            dataT[pointT.x][pointT.y] = 2;
                        }
                    }
                }
            }
        }
        context.putImageData(imageDataO, 0, 0);
    } else {
        binarize(100);
    }
}

binarize = function(thresh) {
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    //Have to redraw image and then scrape data
    context.drawImage(imageObj, 0, 0);
    var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;
    for (var i = 0; i < data.length; i +=4) {
        //Brightness is the greyscale value for the given pixel
        var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
        
        // Binarize image (set to black or white)
        if (brightness > thresh) {
            data[i] = WHITE;
            data[i + 1] = WHITE;
            data[i + 2] = WHITE;
        } else {
            data[i] = BLACK;
            data[i + 1] = BLACK;
            data[i + 2] = BLACK;
        }
    }
    //Draw binarized image
    context.putImageData(imageData, 0, 0);
}
