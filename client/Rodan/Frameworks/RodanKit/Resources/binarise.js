(function ($) {
    //Setup
    $(document).ready(function () {
        "use strict";
        var viewWidth, defThresh, G, rScale, gScale, bScale, globalThresh, boxX, boxY, imageObj, imagePrev, imageThumb, stage, t1;
        viewWidth = 700;
        //Default threshold before user input
        defThresh = 127;
        //Maximum value for greyness (white)
        G = 255;
        //Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
        rScale = 0.2989;
        gScale = 0.5870;
        bScale = 0.1140;
        globalThresh = 0;
        boxX = 0;
        boxY = 0;
        
        //Image drawn to viewport
        imageObj = new Image();
        //Image used for brink thresholding
        imagePrev = new Image();
        //Image used for viewport controller
        imageThumb = new Image();
        
        // Generates a PMF (Probability Mass Function) for the given image (required for Brink)
        function genPMF(imageO, canvas) {
            var canvas, context, i, imageData, data, pmf, brightness;
            // var canvas = document;  <- Canvas is overridden below?
            context = canvas.getContext("2d");
            i = 0;

            //Have to redraw image and then scrape data
            context.drawImage(imageO, 0, 0);
            imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            data = imageData.data;
            pmf = [];
            for (i = 0; i <= G; i++) {
                pmf[i] = 0;
            }
            for (i = 0; i < data.length; i += 4) {
                //Brightness is the greyscale value for the given pixel
                brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
                pmf[Math.round(brightness)]++;
            }

            // Normalize PMF values to total 1
            for (i = 0; i < pmf.length; i++) {
                pmf[i] /= (data.length / 4);
            }
            return pmf;
        }

        //Johanna's Brink Thresholding function
        function threshBrink(pmf) {
            var Topt, locMin, isMinInit, mF, mB, tmpVec1, tmpVec2, tmpVec3, tmp1, tmp2, tmp3, tmp4, tmpMat1, tmpMat2, i, j;
            Topt = 0;       // threshold value
            isMinInit = 0;  // flat for minimum initialization

            mF = [];        // first foreground moment
            mB = [];        // first background moment

            tmpVec1 = [];   // temporary vector 1
            tmpVec2 = [];   // temporary vector 2
            tmpVec3 = [];   // temporary vector 3

            tmp1 = [];      // temporary matrix 1
            tmp2 = [];      // temporary matrix 2
            tmp3 = [];      // temporary matrix 3
            tmp4 = [];      // temporary matrix 4

            tmpMat1 = [];   // local temporary matrix 1
            tmpMat2 = [];   // local temporary matrix 2

            i = 0;
            j = 0;

            //2-dimensionalize matrices
            for (i = 0; i < 256; i++) {
                tmp1[i] = [];
                tmp2[i] = [];
                tmp3[i] = [];
                tmp4[i] = [];

                tmpMat1[i] = [];
                tmpMat2[i] = [];
            }

            // compute foreground moment
            mF[0] = 0.0;
            for (i = 1; i < 256; i++) {
                mF[i] = i * pmf[i] + mF[i - 1];
            }
            // compute background moment
            mB = mF.slice(0);

            for (i = 0; i < 256; i++) {
                mB[i] = mF[255] - mB[i];
            }
            // compute brink entropy binarisation
            for (i = 0; i < 256; i++) {
                for (j = 0; j < 256; j++) {
                    tmp1[i][j] = mF[j] / i;

                    if ((mF[j] === 0) || (i === 0)) {
                        tmp2[i][j] = 0.0;
                        tmp3[i][j] = 0.0;
                    } else {
                        tmp2[i][j] = Math.log(tmp1[i][j]);
                        tmp3[i][j] = Math.log(1.0 / tmp1[i][j]);
                    }
                    tmp4[i][j] = pmf[i] * (mF[j] * tmp2[i][j] + i * tmp3[i][j]);
                }
            }

            // compute the diagonal of the cumulative sum of tmp4 and store result in tmpVec1
            tmpMat1[0] = tmp4[0].slice(0);      // copies first row of tmp4 to the first row of tmpMat1
            for (i = 1; i < 256; i++) {      // get cumulative sum
                for (j = 0; j < 256; j++) {
                    tmpMat1[i][j] = tmpMat1[i - 1][j] + tmp4[i][j];
                }
            }
            for (i = 0; i < 256; i++) {         // set to diagonal
                tmpVec1[i] = tmpMat1[i][i];     // tmpVec1 is now the diagonal of the cumulative sum of tmp4
            }

            // same operation but for background moment, NOTE: tmp1 through tmp4 get overwritten
            for (i = 0; i < 256; i++) {
                for (j = 0; j < 256; j++) {
                    tmp1[i][j] = mB[j] / i;     // tmpb0 = m_b_rep ./ g_rep;
                    if ((mB[j] === 0) || (i === 0)) {
                        tmp2[i][j] = 0.0;       // replace inf or NaN values with 0
                        tmp3[i][j] = 0.0;
                    } else {
                        tmp2[i][j] = Math.log(tmp1[i][j]);
                        tmp3[i][j] = Math.log(1.0 / tmp1[i][j]);
                    }
                    tmp4[i][j] = pmf[i] * (mB[j] * tmp2[i][j] + i * tmp3[i][j]);
                }
            }

            // sum columns, subtract diagonal of cumulative sum of tmp4
            tmpVec2 = tmp4[0].slice(0);         // copies first row of tmp4 to the first row of tmpMat2
            for (i = 0; i < 256; i++) {
                for (j = 0; j < 256; j++) {
                    tmpVec2[j] += tmp4[i][j];   // sums of columns of tmp4 and store result in tmpVec2
                }
            }
            // compute the diagonal of the cumulative sum of tmp4 and store result in tmpVec1
            tmpMat2[0] = tmp4[0].slice(0);      // copies first row of tmp4 to the first row of tmpMat2
            for (i = 1; i < 256; i++) {        // get cumulative sum
                for (j = 0; j < 256; j++) {
                    tmpMat2[i][j] = tmpMat2[i - 1][j] + tmp4[i][j];
                }
            }
            for (i = 0; i < 256; i++) {         // set to diagonal
                tmpVec3[i] = tmpMat2[i][i];     // tmpVec3 is now the diagonal of the cumulative sum of tmpMat2
            }
            for (i = 0; i < 256; i++) {
                tmpVec2[i] -= tmpVec3[i];
            }
            for (i = 0; i < 256; i++) {
                tmpVec1[i] += tmpVec2[i];
            }
            // calculate the threshold value
            for (i = 0; i < 256; i++) {
                if (mF[i] !== 0 && mB[i] !== 0) {
                    if ((isMinInit === 0) || (tmpVec1[i] < locMin)) {
                        isMinInit = 1;
                        locMin = tmpVec1[i];    // gets a new minimum
                        Topt = i;
                    }
                }
            }
            // return optimal threshold
            return Topt;
        }

        //Binarises data, splitting foreground and background at a given brightness level
        function binarise(imageO, canvas, thresh, x, y) {
            var context, imageData, data, i, brightness;
            if (!x) {
                x = 0;
            }
            if (!y) {
                y = 0;
            }
            context = canvas.getContext("2d");
            defThresh = thresh;
            //Have to redraw image and then scrape data
            context.drawImage(imageO, x, y, canvas.width, canvas.height, 0, 0, canvas.width, canvas.height);
            imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            data = imageData.data;
            for (i = 0; i < data.length; i += 4) {
                //Brightness is the greyscale value for the given pixel
                brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
                // binarise image (set to black or white)
                if (brightness > thresh) {
                    data[i] = G;
                    data[i + 1] = G;
                    data[i + 2] = G;
                } else {
                    data[i] = 0;
                    data[i + 1] = 0;
                    data[i + 2] = 0;
                }
            }
            //Draw binarised image
            context.putImageData(imageData, 0, 0);
        }

        //Calculate initial threshold with the Brink formula and draw binarised image
        imageThumb.onload = function () {
            var scaleVal, layer, image, layerB, boxWidth, viewBox, canvas, context, bodyDOM,
                pMouseDown, vMouseDown, vInitX, vInitY;
            scaleVal = imageThumb.width / imageObj.width;
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
                alpha: 0.2,
                draggable: false,
                dragBounds: {
                    top: 0,
                    left: 0,
                    right: imageThumb.width - boxWidth,
                    bottom: imageThumb.height - boxWidth
                },
                name: 'viewBox'
            });

            layerB.add(viewBox);
            stage.add(layerB);

            canvas = document.getElementById("image-viewport");
            context = canvas.getContext("2d");
            bodyDOM = document.getElementsByTagName("body")[0];
            
            window.onresize = function() {
                // console.log("here");
                // console.log($(window).height());
                // viewWidth += $(window).height() - (canvas.offsetTop + viewWidth) - 10;
                // canvas.width = viewWidth;
                // canvas.height = viewWidth;
                // $("#slider").width(viewWidth);
                // boxWidth = viewWidth * scaleVal;
                // viewBox.setWidth(boxWidth);
                // viewBox.setHeight(boxWidth);
                // viewBox.setDragBounds({
                //     top: 0,
                //     left: 0,
                //     right: imageThumb.width - boxWidth,
                //     bottom: imageThumb.height - boxWidth
                // });
                // layerB.draw();
                // boxX = viewBox.getX() / scaleVal;
                // boxY = viewBox.getY() / scaleVal;
                // binarise(imageObj, canvas, defThresh, boxX, boxY);
            }
            
            pMouseDown = false;

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
                    binarise(imageObj, canvas, defThresh, boxX, boxY);
                }
            }

            function pClickDown(e) {
                pMouseDown = true;
                pMoveBox(e);
            }

            image.on("mousedown", pClickDown);
            viewBox.on("mousedown", pClickDown);

            vMouseDown = false;
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
                    binarise(imageObj, canvas, defThresh, boxX, boxY);
                }
            });
            bodyDOM.addEventListener("mouseup", function (e) {
                pMouseDown = false;
                vMouseDown = false;
            });
        };

        imageObj.onload = function () {
            var canvas, context, pmf;
            canvas = document.getElementById("image-viewport");
            viewWidth += $(window).height() - (canvas.offsetTop + viewWidth) - 10;
            canvas.width = viewWidth;
            canvas.height = viewWidth;
            binarise(imageObj, canvas, defThresh);
            //Manually set inital value for slider
            $("#slider").width(viewWidth);
            imageThumb.src = $("#image-thumb").attr("src");
        };
        
        imagePrev.onload = function () {
            var canvas, context, pmf;
            canvas = document.getElementById("image-preview");
            context = canvas.getContext("2d");
            canvas.width = imagePrev.width;
            canvas.height = imagePrev.height;
            pmf = genPMF(imagePrev, canvas);
            defThresh = threshBrink(pmf);
            $("#slider").slider("value", defThresh);
            canvas.parentNode.removeChild(canvas);
            imageObj.src = $("#image-full").attr("src");
        }
        imagePrev.src = $("#image-mid").attr("src");

        //jQuery slider definition for threshold controller
        $("#slider").slider({
            animate: true,
            min: 0,
            max: G,
            orientation: "horizontal",
            step: 1,
            value: defThresh,
            range: false,
            slide: function (event, ui) {
                defThresh = ui.value;
                binarise(imageObj, document.getElementById("image-viewport"), defThresh, boxX, boxY);
            }
        });

        $('#form').submit(function () {
            $('#threshold-input').val(defThresh);
        });
    });
})(jQuery)