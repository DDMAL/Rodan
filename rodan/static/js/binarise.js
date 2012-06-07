//Default threshold before user input
var defThresh = 127;
//Maximum value for greyness
var G = 255;
//Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
var rScale = 0.2989;
var gScale = 0.5870;
var bScale = 0.1140;
var widthLim = 750;
var heightLim = 750;
var imageObj;
var globalThresh = 0;

//Setup
$(document).ready(function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarised image
    imageObj.onload = initImage;
    
    imageObj.src = $("#image-original").attr("src");
    
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
            binarise(defThresh);
        }
    });

    $('#binarise-form').submit(function () {
        $('#threshold-input').val(defThresh);
    });
});

initImage = function() {
    //Adjust size of canvas to fit image
    $("#image-preview").attr("width", imageObj.width);
    $("#image-preview").attr("height", imageObj.height);
    if (imageObj.width > widthLim || imageObj.height > heightLim) {
        var canvas = document.getElementById("image-preview");
        var context = canvas.getContext("2d");
        var scaleVal = widthLim / imageObj.width;
        canvas.width = canvas.width * scaleVal;
        canvas.height = canvas.height * scaleVal;
        imageObj.height *= scaleVal;
        imageObj.width *= scaleVal;
        context.scale(scaleVal, scaleVal);
    }
    var pmf = genPMF(imageObj);
    defThresh = threshBrink(pmf);
    binarise(defThresh);

    //Manually set inital value for slider
    $("#slider").slider("value", defThresh);
    $("#slider").width(imageObj.width * 2);
}

//binarises data, splitting foreground and background at a given brightness level
binarise = function(thresh) {
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    $("#thresh_value").attr("value", thresh);
    $("#thresh_disp").text(thresh);
    globalThresh = thresh;
    //Have to redraw image and then scrape data
    context.drawImage(imageObj, 0, 0);
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
}

// Generates a PMF (Probability Mass Function) for the given image
genPMF = function(imageObj) {
    var canvas = document
    var canvas = document.getElementById("image-preview");
    var context = canvas.getContext("2d");
    
    //Have to redraw image and then scrape data
    context.drawImage(imageObj, 0, 0);
    var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;
    var pmf = new Array(G + 1);
    for (var i = 0; i < pmf.length; i++)
        pmf[i] = 0;
    for (var i = 0; i < data.length; i +=4) {
        //Brightness is the greyscale value for the given pixel
        var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
        pmf[Math.round(brightness)]++;
    }
    // Normalize PMF values to total 1
    for (var i = 0; i < pmf.length; i++)
        pmf[i] /= (data.length / 4);
    return pmf;
}

//Johanna's Brink Thresholding function
threshBrink = function(pmf) {
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
    
    //2-dimensionalize matrices
    for (var i = 0; i < 256; i++) {
        tmp1[i] = new Array(256);
        tmp2[i] = new Array(256);
        tmp3[i] = new Array(256);
        tmp4[i] = new Array(256);
        
        tmpMat1[i] = new Array(256);
        tmpMat2[i] = new Array(256);
    }
    
    // compute foreground moment
    mF[0] = 0.0;
    for (var i = 1; i < 256; i++)
        mF[i] = i * pmf[i] + mF[i - 1];
    
    // compute background moment
    mB = mF.slice(0);
    
    for (var i = 0; i < 256; i++)
        mB[i] = mF[255] - mB[i];
    
    // compute brink entropy binarisation
    for (var i = 0; i < 256; i++) {
        for (var j = 0; j < 256; j++) {
            tmp1[i][j] = mF[j] / i;
            if ((mF[j] == 0) || (i == 0)) {
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
    for (var i = 1; i < 256; i++)       // get cumulative sum
        for (var j = 0; j < 256; j++)
            tmpMat1[i][j] = tmpMat1[i - 1][j] + tmp4[i][j];
    for (var i = 0; i < 256; i++)       // set to diagonal
        tmpVec1[i] = tmpMat1[i][i];     // tmpVec1 is now the diagonal of the cumulative sum of tmp4
    
    
    // same operation but for background moment, NOTE: tmp1 through tmp4 get overwritten
    for (var i = 0; i < 256; i++) {
        for (var j = 0; j < 256; j++) {
            tmp1[i][j] = mB[j] / i;     // tmpb0 = m_b_rep ./ g_rep;
            if ((mB[j] == 0) || (i == 0)) {
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
    for (var i = 0; i < 256; i++)
        for (var j = 0; j < 256; j++)
            tmpVec2[j] += tmp4[i][j];   // sums of columns of tmp4 and store result in tmpVec2
    
    // compute the diagonal of the cumulative sum of tmp4 and store result in tmpVec1
    tmpMat2[0] = tmp4[0].slice(0);      // copies first row of tmp4 to the first row of tmpMat2	
    for (var i = 1; i < 256; i++)       // get cumulative sum
        for (var j = 0; j < 256; j++)
            tmpMat2[i][j] = tmpMat2[i - 1][j] + tmp4[i][j];
    for (var i = 0; i < 256; i++)       // set to diagonal
        tmpVec3[i] = tmpMat2[i][i];     // tmpVec3 is now the diagonal of the cumulative sum of tmpMat2
    
    for (var i = 0; i < 256; i++)
        tmpVec2[i] -= tmpVec3[i];
    for (var i = 0; i < 256; i++)
        tmpVec1[i] += tmpVec2[i];
    
    // calculate the threshold value
    for (var i = 0; i < 256; i++) {
        if (mF[i] != 0 && mB[i] != 0) {
            if ((isMinInit == 0) || (tmpVec1[i] < locMin)) {
                isMinInit = 1;
                locMin = tmpVec1[i];    // gets a new minimum
                Topt = i;
            }
        }
    }
    
    // return optimal threshold
    return Topt;
}
