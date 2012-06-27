//Setup
$(document).ready(function() {
    //ImageData object storing full-sized image
    var imageObj = new Image();
    //ImageData object storing small thumbnail
    var imageThumb = new Image();
    //Constant for black rgb value
    var BLACK = 0;
    //Consdtant for white rgb value
    var WHITE = 255;
    //Scale values taken from Matlab, used as coefficients for greycsaling
    var rScale = 0.2989;
    var gScale = 0.5870;
    var bScale = 0.1140;
    //Default speckle size
    var defSize = 0;
    //Width (square) of viewport
    var viewWidth = 500;
    //Current x and y coordinates of the frame of the viewport, relative to the full image
    var boxX = 0;
    var boxY = 0;
    
    //Wrapper for (x, y) coordinate pair
    function Point(x, y) {
        this.x = x;
        this.y = y;
    }

    //Object for storing the image data for ease of access (ie. with coordinate pairs)
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
    
    //Thumbnail post-loading functions, which occur after the full image is loaded
    imageThumb.onload = function() {
        //Instantiation of KinteticJS objects
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

        //Ratio of thumbnail size to full image size
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
            draggable: false,
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
        
        //Assignment of mouse behaviours to canvases
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        var bodyDOM = document.getElementsByTagName("body")[0];
        //Bool for whether mousedown started in the thumbnail frame
        var pMouseDown = false;

        //Move viewport and despeckle
        var setBox = function() {
            boxX = viewBox.getX() / scaleVal;
            boxY = viewBox.getY() / scaleVal;
            despeckle(defSize, boxX, boxY);
        };
        
        //Move thumbnail box
        var pMoveBox = function(e) {
            var pos = stage.getMousePosition(e);
            if (pos != undefined) {
                var boxWidth = viewWidth * scaleVal;
                pos.x -= (boxWidth / 2);
                pos.y -= (boxWidth / 2);
                if (pos.x < 0) {
                    pos.x = 0;
                } else if ((pos.x + boxWidth) > imageThumb.width) {
                    pos.x = imageThumb.width - boxWidth;
                }
                if (pos.y < 0) {
                    pos.y = 0;
                } else if ((pos.y + boxWidth) > imageThumb.height) {
                    pos.y = imageThumb.height - boxWidth;
                }
                viewBox.setX(pos.x);
                viewBox.setY(pos.y);
                viewBox.getLayer().draw();
                boxX = viewBox.getX() / scaleVal;
                boxY = viewBox.getY() / scaleVal;
                binarise(100, boxX, boxY);
            }
        };

        //
        image.on("mousedown", function(e) {
            pMoveBox(e);
            pMouseDown = true;
        });

        viewBox.on("mousedown", function() {
            pMouseDown = true;
        });
        
        //Bool for whether mousedown started in the viewport
        var vMouseDown = false;
        //Previous mouse coordinates
        var vInitX = 0;
        var vInitY = 0;
        canvas.addEventListener("mousedown", function(e) {
            vMouseDown = true;
            vInitX = e.clientX;
            vInitY = e.clientY;
        });
        bodyDOM.addEventListener("mousemove", function(e) {
            if (pMouseDown) {
                pMoveBox(e);
            } else if (vMouseDown) {
                var dX = e.clientX - vInitX;
                var dY = e.clientY - vInitY;
                
                vInitX = e.clientX;
                vInitY = e.clientY;
                
                var boxWidth = viewWidth * scaleVal;
                var newX = viewBox.getX() - (dX * scaleVal);
                var newY = viewBox.getY() - (dY * scaleVal);
                if (newX < 0) {
                    newX = 0;
                } else if ((newX + boxWidth) > imageThumb.width) {
                    newX = imageThumb.width - boxWidth;
                }
                if (newY < 0) {
                    newY = 0;
                } else if ((newY + boxWidth) > imageThumb.height) {
                    newY = imageThumb.height - boxWidth;
                }
                
                viewBox.setX(newX);
                viewBox.setY(newY);
                viewBox.getLayer().draw();
                boxX = viewBox.getX() / scaleVal;
                boxY = viewBox.getY() / scaleVal;
                binarise(100, boxX, boxY);
            }
        });
        bodyDOM.addEventListener("mouseup", function(e) {
            if (pMouseDown) {
                pMouseDown = false;
                setBox();
            } else if (vMouseDown) {
                vMouseDown = false;
                var dX = e.clientX - vInitX;
                var dY = e.clientY - vInitY;
                
                var boxWidth = viewWidth * scaleVal;
                var newX = viewBox.getX() - (dX * scaleVal);
                var newY = viewBox.getY() - (dY * scaleVal);
                if (newX < 0) {
                    newX = 0;
                } else if ((newX + boxWidth) > imageThumb.width) {
                    newX = imageThumb.width - boxWidth;
                }
                if (newY < 0) {
                    newY = 0;
                } else if ((newY + boxWidth) > imageThumb.height) {
                    newY = imageThumb.height - boxWidth;
                }
                
                viewBox.setX(newX);
                viewBox.setY(newY);
                viewBox.getLayer().draw();
                boxX = viewBox.getX() / scaleVal;
                boxY = viewBox.getY() / scaleVal;
                despeckle(defSize, boxX, boxY);
            }
        });
    };
    
    
    imageObj.onload = function() {
        //Adjust size of canvas to fit image
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        canvas.width = viewWidth;
        canvas.height = viewWidth;
        binarise(100);
        $("#slider").width(viewWidth);
        imageThumb.src = $("#image-thumb").attr("src");
    };

    

    imageObj.src = $("#image-full").attr("src");

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
