//Setup
$(document).ready(function() {
    var viewWidth = 500;
    //Default threshold before user input
    var defThresh = 127;
    //Maximum value for greyness
    var G = 255;
    //Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
    var rScale = 0.2989;
    var gScale = 0.5870;
    var bScale = 0.1140;
    var imageObj;
    var globalThresh = 0;
    var boxX = 0;
    var boxY = 0;

    var imageObj = new Image();
    var imageThumb = new Image();
    var stage;
    //Calculate initial threshold with the Brink formula and draw binarised image

    imageObj.onload = function() {
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        canvas.width = viewWidth;
        canvas.height = viewWidth;
        var pmf = genPMF(imageObj);
        defThresh = threshBrink(pmf);
        binarise(defThresh);
        //Manually set inital value for slider
        $("#slider").slider("value", defThresh);
        $("#slider").width(viewWidth);
    };

    imageThumb.onload = function() {
        var scaleVal = imageThumb.width / imageObj.width;

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

        var moveBox = function() {
            var canvas = document.getElementById("image-viewport");
            var context = canvas.getContext("2d");
            boxX = viewBox.getX() / scaleVal;
            boxY = viewBox.getY() / scaleVal;
            binarise(defThresh, boxX, boxY);
        };

        viewBox.on("dragmove", moveBox);

        image.on("mousedown", function(e) {
            var boxWidth = viewWidth * scaleVal;
            var mousePos = stage.getUserPosition(e);
            var boxPosX = mousePos.x - (boxWidth / 2);
            var boxPosY = mousePos.y - (boxWidth / 2);
            if (mousePos.x < (boxWidth / 2)) {
                boxPosX = 0;
            } else if ((mousePos.x + (boxWidth / 2)) > imageThumb.width) {
                boxPosX = imageThumb.width - boxWidth;
            }
            if (mousePos.y < (boxWidth / 2)) {
                boxPosY = 0;
            } else if ((mousePos.y + (boxWidth / 2)) > imageThumb.height) {
                boxPosY = imageThumb.height - boxWidth;
            }
            viewBox.setX(boxPosX);
            viewBox.setY(boxPosY);
            viewBox.getLayer().draw();
            moveBox();
        });
    };

    imageObj.src = $("#image-full").attr("src");
    imageThumb.src = $("#image-thumb").attr("src");

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
        $("#thresh_value").attr("value", thresh);
        $("#thresh_disp").text(thresh);
        defThresh = thresh;
        //Have to redraw image and then scrape data
        context.drawImage(imageObj, -x, -y);
        var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        var data = imageData.data;
        for (var i = 0; i < data.length; i +=4) {
            //Brightness is the greyscale value for the given pixel
            var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];

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
    };

    // Generates a PMF (Probability Mass Function) for the given image
    var genPMF = function(imageObj) {
        // var canvas = document;  <- Canvas is overridden below?
        var canvas = document.getElementById("image-viewport");
        var context = canvas.getContext("2d");
        var i = 0;

        //Have to redraw image and then scrape data
        context.drawImage(imageObj, 0, 0);
        var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        var data = imageData.data;
        var pmf = [];
        for (i = 0; i <= G; i++)
            pmf[i] = 0;

        for (i = 0; i < data.length; i +=4) {
            //Brightness is the greyscale value for the given pixel
            var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
            pmf[Math.round(brightness)]++;
        }

        // Normalize PMF values to total 1
        for (i = 0; i < pmf.length; i++)
            pmf[i] /= (data.length / 4);
        return pmf;
    };

    //jQuery slider definition for threshold controller
    $("#slider").slider({
        animate: true,
        min: 0,
        max: G,
        orientation: "horizontal",
        step: 1,
        value: defThresh,
        range: false,
        slide: function(event, ui) {
            defThresh = ui.value;
            binarise(defThresh, boxX, boxY);
        }
    });

    //Johanna's Brink Thresholding function
    var threshBrink = function(pmf) {
        var Topt = 0;       // threshold value
        var locMin;         // local minimum
        var isMinInit = 0;  // flat for minimum initialization

        var mF = new Array(256);        // first foreground moment
        var mB = new Array(256);        // first background moment

        var tmpVec1 = new Array(256);   // temporary vector 1
        var tmpVec2 = new Array(256);   // temporary vector 2
        var tmpVec3 = new Array(256);   // temporary vector 3

        var tmp1 = new Array(256);      // temporary matrix 1
        var tmp2 = new Array(256);      // temporary matrix 2
        var tmp3 = new Array(256);      // temporary matrix 3
        var tmp4 = new Array(256);      // temporary matrix 4

        var tmpMat1 = new Array(256);   // local temporary matrix 1
        var tmpMat2 = new Array(256);   // local temporary matrix 2

        var i = 0;
        var j = 0;

        //2-dimensionalize matrices
        for (i = 0; i < 256; i++) {
            tmp1[i] = new Array(256);
            tmp2[i] = new Array(256);
            tmp3[i] = new Array(256);
            tmp4[i] = new Array(256);

            tmpMat1[i] = new Array(256);
            tmpMat2[i] = new Array(256);
        }

        // compute foreground moment
        mF[0] = 0.0;
        for (i = 1; i < 256; i++)
            mF[i] = i * pmf[i] + mF[i - 1];

        // compute background moment
        mB = mF.slice(0);

        for (i = 0; i < 256; i++)
            mB[i] = mF[255] - mB[i];

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
        for (i = 0; i < 256; i++)       // set to diagonal
            tmpVec1[i] = tmpMat1[i][i];     // tmpVec1 is now the diagonal of the cumulative sum of tmp4


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
        for (i = 0; i < 256; i++)
            for (j = 0; j < 256; j++)
                tmpVec2[j] += tmp4[i][j];   // sums of columns of tmp4 and store result in tmpVec2

        // compute the diagonal of the cumulative sum of tmp4 and store result in tmpVec1
        tmpMat2[0] = tmp4[0].slice(0);      // copies first row of tmp4 to the first row of tmpMat2
        for (i = 1; i < 256; i++)       // get cumulative sum
            for (j = 0; j < 256; j++)
                tmpMat2[i][j] = tmpMat2[i - 1][j] + tmp4[i][j];
        for (i = 0; i < 256; i++)       // set to diagonal
            tmpVec3[i] = tmpMat2[i][i];     // tmpVec3 is now the diagonal of the cumulative sum of tmpMat2

        for (i = 0; i < 256; i++)
            tmpVec2[i] -= tmpVec3[i];
        for (i = 0; i < 256; i++)
            tmpVec1[i] += tmpVec2[i];

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
    };

    $('#binarise-form').submit(function () {
        $('#threshold-input').val(defThresh);
    });
});
