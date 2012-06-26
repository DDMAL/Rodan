//Setup
$(document).ready(function() {
    var imageObj;
    var imageThumb;
    var BLACK = 0;
    var WHITE = 255;
    var rScale = 0.2989;
    var gScale = 0.5870;
    var bScale = 0.1140;
    var defSize = 0;
    var viewWidth = 500;
    var boxX = 0;
    var boxY = 0;

    function Point(x, y) {
        this.x = x;
        this.y = y;
    }

    function IData(data, canvas) {
        this.data = data;
        this.getPoint = function(x, y) {
            var convX = x * 4;
            var convY = y * canvas.width * 4;
            return this.data[convX + convY];
        };
        this.setPoint = function(x, y, val) {
            var convX = x * 4;
            var convY = y * canvas.width * 4;
            this.data[convX + convY] = val;
            this.data[convX + convY + 1] = val;
            this.data[convX + convY + 2] = val;
        };
        this.isBlack = function(x, y) {
            return this.getPoint(x, y) === BLACK;
        };
    }
    
    imageObj = new Image();
    imageThumb = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = function() {
        //Adjust size of canvas to fit image
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        canvas.width = viewWidth;
        canvas.height = viewWidth;
        binarise(100);
        $("#slider").width(viewWidth);
    };
    
    imageThumb.onload = function() {
        stage = new Kinetic.Stage({
            container: "image-miniframe",
            width: imageThumb.width,
            height: imageThumb.height,
        });
        var layer = new Kinetic.Layer();
        var image = new Kinetic.Image({
            x: 0,
            y: 0,
            width: imageThumb.width,
            height: imageThumb.height,
            image: imageThumb,
            stroke: 'black',
            strokewidth: 2
        });

        layer.add(image);
        stage.add(layer);
        
        var scaleVal = imageThumb.width / imageObj.width;
        
        var layerB = new Kinetic.Layer();
        
        var boxWidth = viewWidth * scaleVal;
        var viewBox = new Kinetic.Rect({
            x: 0,
            y: 0,
            width: boxWidth,
            height: boxWidth,
            fill: 'blue',
            stroke: 'black',
            strokeWidth: 2,
            alpha: .2,
            draggable: true,
            dragBounds: {
                top: 0,
                left: 0,
                right: imageThumb.width - boxWidth,
                bottom: imageThumb.height - boxWidth,
            },
            name:'viewBox'
        });
        
        layerB.add(viewBox);
        stage.add(layerB);
        
        viewBox.on("dragend", function() {
            var canvas = document.getElementById("image-viewport");
            var context = canvas.getContext("2d");
            boxX = viewBox.getX() / scaleVal;
            boxY = viewBox.getY() / scaleVal;
            despeckle(defSize, boxX, boxY);
        });
    };
    
    imageObj.src = $("#image-full").attr("src");
    imageThumb.src = $("#image-thumb").attr("src");
    
    var despeckle = function(size, x, y) {
        defSize = size;
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        binarise(100, x, y);
        if (size > 0) {
            var imageDataO = context.getImageData(0, 0, canvas.width, canvas.height);
            var dataO = new IData(imageDataO.data, canvas);

            var dataT = [];
            for (var i = 0; i < canvas.width; i++) {
                dataT[i] = [];
                for (var j = 0; j < canvas.height; j++) {
                    dataT[i][j] = 0;
                }
            }

            var pixelQueue = [];
            for (var y = 0; y < canvas.height; ++y) {
                for (var x = 0; x < canvas.width; ++x) {
                    if (dataT[x][y] == 0 && dataO.isBlack(x, y)) {
                        pixelQueue = [];
                        pixelQueue.push(new Point(x, y));
                        var bail = false;
                        dataT[x][y] = 1;
                        for (var i = 0; (i < pixelQueue.length) && (pixelQueue.length < size); ++i) {
                            var center = pixelQueue[i];
                            for (var y2 = ((center.y > 0) ? center.y - 1 : 0); (y2 < Math.min(center.y + 2, canvas.height)); ++y2) {
                                for (var x2 = ((center.x > 0) ? center.x - 1 : 0); (x2 < Math.min(center.x + 2, canvas.width)); ++x2) {
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
                        if ((!bail) && (pixelQueue.length < size)) {
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
        }
    }
    
    //binarises data, splitting foreground and background at a given brightness level
    var binarise = function(thresh, x, y) {
        if (!x) {
            x = 0;
        }
        if (!y) {
            y = 0;
        }
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        //Have to redraw image and then scrape data
        context.drawImage(imageObj, -x, -y);
        var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        var data = imageData.data;
        for (var i = 0; i < data.length; i +=4) {
            //Brightness is the greyscale value for the given pixel
            var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];

            // binarise image (set to black or white)
            if (brightness > thresh) {
                data[i] = 255;
                data[i + 1] = 255;
                data[i + 2] = 255;
            } else {
                data[i] = 0;
                data[i + 1] = 0;
                data[i + 2] = 0;
            }
        }
        //Draw binarised image
        context.putImageData(imageData, 0, 0);
    };
    
    //jQuery slider definition for threshold controller
    $("#slider").slider({
                        animate: true,
                        min: 0,
                        max: 100,
                        orientation: "horizontal",
                        step: 1,
                        value: 0,
                        range: false,
                        slide: function(event, ui) {despeckle(ui.value, boxX, boxY)},
                        });
                        
    $('#despeckle-form').submit(function () {
        $('#size-input').val(defSize);
    });
});
