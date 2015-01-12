(function ($) {
    "use strict";
    //Setup
    $(document).ready(function () {
        var imageObj, imageThumb, BLACK, WHITE, rScale, gScale, bScale, defSize, viewWidth, boxX, boxY;

        //ImageData object storing full-sized image

        imageObj = new Image();
        imageThumb = new Image();
        //Constant for black rgb value
        BLACK = 0;
        WHITE = 255;
        //Scale values taken from Matlab, used as coefficients for greycsaling
        rScale = 0.2989;
        gScale = 0.5870;
        bScale = 0.1140;
        //Default speckle size
        defSize = 0;
        //Width (square) of viewport
        viewWidth = 700;
        //Current x and y coordinates of the frame of the viewport, relative to the full image
        boxX = 0;
        boxY = 0;



        //binarises data, splitting foreground and background at a given brightness level
        function binarise(thresh, x, y) {
            if (x === undefined) {
                x = 0;
            }
            if (y === undefined) {
                y = 0;
            }
            var canvas, context, imageData, data, dLen, i, brightness;
            canvas = document.getElementById("image-viewport");
            context = canvas.getContext("2d");
            //Have to redraw image and then scrape data
            if (x == 0 && y == 0) {
                context.drawImage(imageObj, x, y);
            } else {
                context.drawImage(imageObj, x, y, canvas.width, canvas.height, 0, 0, canvas.width, canvas.height);
            }
            imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            data = imageData.data;
            dLen = data.length;
            for (i = 0; i < dLen; i += 4) {
                //Brightness is the greyscale value for the given pixel
                brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];

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
        }

        //Despeckling function
        function despeckle(size, dx, dy) {
            if (dx === undefined) {
                dx = 0;
            }
            if (dy === undefined) {
                dy = 0;
            }
            var canvas, context, imageDataO, dataO, w, h, dataT, i, j, x, y, pixelQueue, convX, convY, p, bail,
                center, cX, cY, x2i, y2i, x2Lim, y2Lim, y2, x2, convX2, convY2, p2,
                pointO, pointT, pX, pY;
            defSize = size;
            canvas = document.getElementById("image-viewport");
            context = canvas.getContext("2d");
            binarise(100, dx, dy);
            if (size > 0) {
                imageDataO = context.getImageData(0, 0, canvas.width, canvas.height);
                dataO = imageDataO.data;

                w = canvas.width;
                h = canvas.height;

                dataT = [];
                for (i = 0; i < w; i++) {
                    dataT[i] = [];
                    for (j = 0; j < h; j++) {
                        dataT[i][j] = 0;
                    }
                }

                pixelQueue = [];
                for (y = 0; y < h; y++) {
                    for (x = 0; x < w; x++) {
                        convX = x * 4;
                        convY = y * w * 4;
                        p = convX + convY;
                        if (dataT[x][y] === 0 && dataO[p] === BLACK) {
                            pixelQueue = [];
                            pixelQueue.push(p);
                            bail = false;
                            dataT[x][y] = 1;
                            for (i = 0; (i < pixelQueue.length) && (pixelQueue.length < size); i++) {
                                center = pixelQueue[i];

                                cX = (center % (w * 4)) / 4;
                                cY = (center - (cX * 4)) / (w * 4);
                                x2i = (cX > 0) ? (cX - 1) : 0;
                                y2i = (cY > 0) ? (cY - 1) : 0;

                                x2Lim = Math.min(cX + 2, w);
                                y2Lim = Math.min(cY + 2, h);
                                for (y2 = y2i; y2 < y2Lim; y2++) {
                                    for (x2 = x2i; x2 < x2Lim; x2++) {
                                        if (dataT[x2][y2] === 2) {
                                            bail = true;
                                            break;
                                        }
                                        convX2 = x2 * 4;
                                        convY2 = y2 * w * 4;
                                        p2 = convX2 + convY2;
                                        if (dataT[x2][y2] === 0 && dataO[p2] === BLACK) {
                                            dataT[x2][y2] = 1;
                                            pixelQueue.push(p2);
                                        }
                                    }
                                    if (bail) {
                                        break;
                                    }
                                }
                                if (bail) {
                                    break;
                                }
                            }
                            if ((!bail) && (pixelQueue.length < size)) {
                                while (pixelQueue.length > 0) {
                                    pointO = pixelQueue.pop();
                                    dataO[pointO] = WHITE;
                                    dataO[pointO + 1] = WHITE;
                                    dataO[pointO + 2] = WHITE;
                                }
                            } else {
                                while (pixelQueue.length > 0) {
                                    pointT = pixelQueue.pop();
                                    pX = (pointT % (w * 4)) / 4;
                                    pY = (pointT - (pX * 4)) / (w * 4);
                                    dataT[pX][pY] = 2;
                                }
                            }
                        }
                    }
                }
                context.putImageData(imageDataO, 0, 0);
            }
        }

        //Thumbnail post-loading functions, which occur after the full image is loaded
        imageThumb.onload = function () {
            var stage, layer, image, scaleVal, layerB, boxWidth, viewBox, canvas, context, bodyDOM,
                pMouseDown, vMouseDown, vInitX, vInitY;
            //Instantiation of KinteticJS objects
            stage = new Kinetic.Stage({
                container: "image-miniframe",
                width: imageThumb.width,
                height: imageThumb.height
            });
            layer = new Kinetic.Layer();
            image = new Kinetic.Image({
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
            scaleVal = imageThumb.width / imageObj.width;

            layerB = new Kinetic.Layer();

            boxWidth = viewWidth * scaleVal;
            viewBox = new Kinetic.Rect({
                x: 0,
                y: 0,
                width: boxWidth,
                height: boxWidth,
                fill: 'blue',
                stroke: 'black',
                strokeWidth: 2,
                opacity: 0.2,
                draggable: false,
                dragBoundfunc: function(pos) {
                    var newX = pos.x < 0 ? 0 : pos.x;
                    newX = newX > (imageThumb.width - boxWidth) ? (imageThumb.width - boxWidth) : newX;
                    var newY = pos.y < 0 ? 0 : pos.y;
                    newY = newY > (imageThumb.height - boxWidth) ? (imageThumb.height - boxWidth) : newY;
                    return {
                        x: newX,
                        y: newY
                    };
                },
                name: 'viewBox'
            });

            layerB.add(viewBox);
            stage.add(layerB);

            //Assignment of mouse behaviours to canvases
            canvas = document.getElementById("image-viewport");
            context = canvas.getContext("2d");
            bodyDOM = document.getElementsByTagName("body")[0];

            function resizeWindow() {
                viewWidth += $(window).height() - (canvas.offsetTop + viewWidth) - 10;
                canvas.width = viewWidth;
                canvas.height = viewWidth;
                $("#slider").width(viewWidth);
                boxWidth = viewWidth * scaleVal;
                viewBox.setWidth(boxWidth);
                viewBox.setHeight(boxWidth);
                layerB.draw();
                boxX = viewBox.getX() / scaleVal;
                boxY = viewBox.getY() / scaleVal;
                despeckle(defSize, boxX, boxY);
            }

            window.onresize = resizeWindow;

            resizeWindow();

            //Bool for whether mousedown started in the thumbnail frame
            pMouseDown = false;

            //Move viewport and despeckle
            function setBox() {
                boxX = viewBox.getX() / scaleVal;
                boxY = viewBox.getY() / scaleVal;
                despeckle(defSize, boxX, boxY);
            }

            //Move thumbnail box
            function pMoveBox(e) {
                var pos, boxWidth, nX, nY;
                pos = stage.getMousePosition(e);
                if (pos !== undefined) {
                    boxWidth = viewWidth * scaleVal;
                    nX = pos.x - Math.round(boxWidth / 2);
                    nY = pos.y - Math.round(boxWidth / 2);
                    if (nX < 0) {
                        nX = 0;
                    } else if ((nX + boxWidth) > imageThumb.width) {
                        nX = imageThumb.width - boxWidth;
                    }
                    if (nY < 0) {
                        nY = 0;
                    } else if ((nY + boxWidth) > imageThumb.height) {
                        nY = imageThumb.height - boxWidth;
                    }
                    viewBox.setX(nX);
                    viewBox.setY(nY);
                    viewBox.getLayer().draw();
                    boxX = viewBox.getX() / scaleVal;
                    boxY = viewBox.getY() / scaleVal;
                    binarise(100, boxX, boxY);
                }
            }

            //
            image.on("mousedown", function (e) {
                pMoveBox(e);
                pMouseDown = true;
            });

            viewBox.on("mousedown", function () {
                pMouseDown = true;
            });

            //Bool for whether mousedown started in the viewport
            vMouseDown = false;
            //Previous mouse coordinates
            vInitX = 0;
            vInitY = 0;
            canvas.addEventListener("mousedown", function (e) {
                vMouseDown = true;
                vInitX = e.clientX;
                vInitY = e.clientY;
            });
            bodyDOM.addEventListener("mousemove", function (e) {
                if (pMouseDown) {
                    pMoveBox(e);
                } else if (vMouseDown) {
                    var dX, dY, boxWidth, newX, newY;
                    dX = e.clientX - vInitX;
                    dY = e.clientY - vInitY;

                    vInitX = e.clientX;
                    vInitY = e.clientY;

                    boxWidth = viewWidth * scaleVal;
                    newX = viewBox.getX() - (dX * scaleVal);
                    newY = viewBox.getY() - (dY * scaleVal);
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
            bodyDOM.addEventListener("mouseup", function (e) {
                if (pMouseDown) {
                    pMouseDown = false;
                    setBox();
                } else if (vMouseDown) {
                    var dX, dY, boxWidth, newX, newY;
                    vMouseDown = false;
                    dX = e.clientX - vInitX;
                    dY = e.clientY - vInitY;

                    boxWidth = viewWidth * scaleVal;
                    newX = viewBox.getX() - (dX * scaleVal);
                    newY = viewBox.getY() - (dY * scaleVal);
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


        imageObj.onload = function () {
            var canvas, context;
            //Adjust size of canvas to fit image
            canvas = document.getElementById("image-viewport");
            context = canvas.getContext("2d");
            viewWidth += $(window).height() - (canvas.offsetTop + viewWidth) - 10;
            canvas.width = viewWidth;
            canvas.height = viewWidth;
            binarise(100);
            $("#slider").width(viewWidth);
            imageThumb.src = $("#image-thumb").attr("src");
        };

        imageObj.src = $("#image-full").attr("src");

        //jQuery slider definition for threshold controller
        $("#slider").slider({
            animate: true,
            min: 0,
            max: 100,
            orientation: "horizontal",
            step: 1,
            value: 0,
            range: false,
            slide: function (event, ui) {
                $("#cl_size").html(ui.value);
                despeckle(ui.value, boxX, boxY);
                console.log(imageObj.width)
            }
        });
        $('#form').submit(function () {
            var serialized_data = JSON.stringify({
                'cc_size': defSize,
                'image_width': imageObj.width
            });
            $('#serialized-input').val(serialized_data);
        });
    });
})(jQuery)
