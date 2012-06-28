//Default threshold before user input
var defThresh = 127;
//Maximum value for greyness
var imageObj;
var globalThresh = 0;

//Setup
$(document).ready(function() {
    var BLACK = 0;
    var WHITE = 255;
    
    function IData(data, width, height, ulx, uly) {
        this.data = data;
        this.width = width;
        this.height = height;
        if (!ulx) {
            this.ulx = 0;
        }
        if (!uly) {
            this.uly = 0;
        }
        this.getPoint = function(x, y) {
            var convX = x * 4;
            var convY = y * this.width * 4;
            return this.data[convX + convY];
        };
        this.getPixelRGB = function (x, y) {
            var convX = x * 4;
            var convY = y * imageObj.with * 4;
            return new PixelRGB(this.data[convX + convY],
                                this.data[convX + convY + 1],
                                this.data[convX + convY + 2]);
        }
        this.getRGBA = function(x, y) {
            var convX = x * 4;
            var convY = y * imageObj.with * 4;
            var rgba = []
            rgba[0] = this.data[convX + convY];
            rgba[1] = this.data[convX + convY + 1];
            rgba[2] = this.data[convX + convY + 2];
            rgba[3] = this.data[convX + convY + 3];
            return rgba;
        }
        this.setPoint = function(x, y, val) {
            var convX = x * 4;
            var convY = y * imageObj.width * 4;
            this.data[convX + convY] = val;
            this.data[convX + convY + 1] = val;
            this.data[convX + convY + 2] = val;
        };
        this.setPixelRGB = function(x, y, pRGB) {
            var convX = x * 4;
            var convY = y * imageObj.with * 4;
            this.data[convX + convY] = pRGB.r;
            this.data[convX + convY + 1] = pRGB.g;
            this.data[convX + convY + 2] = pRGB.b;
        }
        this.setRGBA = function(x, y, rgba) {
            var convX = x * 4;
            var convY = y * imageObj.with * 4;
            this.data[convX + convY] = rgba[0];
            this.data[convX + convY + 1] = rgba[1];
            this.data[convX + convY + 2] = rgba[2];
            this.data[convX + convY + 3] = rgba[3];
        }
        this.isBlack = function(x, y) {
            return this.getPoint(x, y) === BLACK;
        };
        this.subImage = function(ulx, uly, lrx, lry) {
            var nData = [];
            var nWidth = lrx - ulx;
            var nHeight = lry - uly;
            for (var y = uly; y < lry; y++) {
                for (var x = ulx; x < lrx; x++) {
                    var rgba = this.getRGBA(x, y);
                    nData.push(rgba[0]);
                    nData.push(rgba[1]);
                    nData.push(rgba[2]);
                    nData.push(rgba[3]);
                }
            }
            return new IData(nData, nWidth, nHeight, ulx + this.ulx, uly + this.uly);
        }
        this.overwriteImage = function(sData, ulx, uly) {
            for (var y = 0; y < sData.height; y++) {
                for (var x = 0; x < sData.width; x++) {
                    this.setRGBA(x + ulx, y + uly, sData.getRGBA(x, y));
                }
            }
        }
    }
    
    function PixelRGB(r, g, b) {
        this.r = r;
        this.g = g;
        this.b = b;
        
        this.scale = function(value) {
            return new PixelRGB(this.r * value, this.g * value, this.b * value);
        }
        
        this.clone = function() {
            return new PixelRGB(this.r, this.g, this.b);
        }
        
        this.add = function(p) {
            return new PixelRGB(this.r + p.r, this.g + p.g, this.b + p.b);
        }
        
        this.divide = function(value) {
            return this.scale(1.0 / value);
        }
    }
    
    imageObj = new Image();
    imageObj.onload = function() {
        //Adjust size of canvas to fit image
        var canvas = document.getElementById("image-preview");
        var context = canvas.getContext("2d");
        canvas.width = imageObj.width;
        canvas.height = imageObj.height;
        context.drawImage(imageObj, 0, 0);
        djvu_threshold();
    };
    
    imageObj.src = $("#image-original").attr("src");
    
    var createBlock = function(width, height) {
        var data = [];
        for (var i = 0; i < (width * height * 4); i++)
            data[i] = 0;
        return new IData(data, width, height);
    }
    
    var djvu_distance = function(x, y) {
        var r = x.r - y.r;
        var g = x.g - y.g;
        var b = x.b - y.b;
        return (0.75*r + g*g + 0.5*b*b);
    }
    
    var djvu_converged = function(fg, bg) {
        return (djvu_distance(fg, bg) < 2);
    }
    
    var djvu_threshold_recurse = function(data, smoothness, minBlockSize, fgData, bgData, fgInit, bgInit, blockSize) {
        var fg = fgInit.clone();
        var bg = bgInit.clone();
        var lastFG, lastBG;
        var fgConverged = false;
        var bgConverged = false;
        var fgInitScaled = fgInit.scale(smoothness);
        var bgInitScaled = bgInit.scale(smoothness);
        var hm = 0;
        do {
            lastFG = fg.clone();
            lastBG = bg.clone();
            var fgAvg = new PixelRGB(0, 0 ,0);
            var bgAvg = new PixelRGB(0, 0, 0);
            var fgCount = 0;
            var bgCount = 0;
            for (var y = 0; y < data.height; y++) {
                for (var x = 0; x < data.width; x++) {
                    var i = data.getPixelRGB(x, y);
                    var fgDist = djvu_distance(i, fg);
                    var bgDist = djvu_distance(i, bg);
                    if (fgDist <= bgDist) {
                        fgAvg = fgAvg.add(i);
                        ++fgCount;
                    } else {
                        bgAvg = bgAvg.add(i);
                        ++bgCount;
                    }
                }
            }
            if (fgCount > 0) {
                fg = (((fgAvg.divide(bgCount)).scale(1.0 - smoothness)).add(fgInitScaled));
                fgConverged = djvu_converged(fg, lastFG);
            } else {
                fgConverged = true;
            }
            if (bgCount > 0) {
                bg = (((bgAvg.divide(bgCount)).scale(1.0 - smoothness)).add(bgInitScaled));
                bgConverged = djvu_converged(bg, lastBG);
            } else {
                bgConverged = true;
            }
        } while (!(fgConverged && bgConverged) && (++hm) < 1);
        
        if (blockSize < minBlockSize) {
            fgData.setPixelRGB((data.ulx / minBlockSize), (data.uly / minBlockSize), fg);
            bgData.setPixelRGB((data.ulx / minBlockSize), (data.uly / minBlockSize), bg);
        } else {
            for (var y = 0; y <= ((data.height - 1) / blockSize); y++) {
                for (var x = 0; x <= ((data.width - 1) / blockSize); x++) {
                    var ulx = x * blockSize;
                    var uly = y * blockSize;
                    var lrx = Math.min((x + 1) * blockSize, data.width);
                    var lry = Math.min((y + 1) * blockSize, data.height);
                    /*data.overwriteImage(ulx, uly,
                                        djvu_threshold_recurse(data.subImage(ulx, uly, lrx, lry),
                                                               smoothness,
                                                               minBlockSize,
                                                               fgData,
                                                               bgData,
                                                               fg,
                                                               bg,
                                                               blockSize / 2));*/
                }
            }
        }
    }
    
    var djvu_threshold_h = function(data, smoothness, maxBlockSize, minBlockSize, blockFactor, fgInit, bgInit) {
        var fgData = createBlock(imageObj.width / (minBlockSize + 1),
                                 imageObj.height / (minBlockSize + 1));
        var bgData = createBlock(imageObj.width / (minBlockSize + 1),
                                 imageObj.height / (minBlockSize + 1));
        
        djvu_threshold_recurse(data, smoothness, minBlockSize, fgData, bgData, fgInit, bgInit, maxBlockSize);
        
        for (var y = 0; y < data.height; y++) {
            for (var x = 0; x < data.width; x++) {
                var xFrac = x / minBlockSize;
                var yFrac = y / minBlockSize;
                var fg = fgData.getPixelRGB(xFrac, yFrac);
                var bg = bgData.getPixelRGB(xFrac, yFrac);
                var fgDist = djvu_distance(data.getPixelRGB(x, y), fg);
                var bgDist = djvu_distance(data.getPixelRGB(x, y), bg);
                if (fgDist <= bgDist)
                    data.setPoint(x, y, BLACK);
                else
                    data.setPoint(x, y, WHITE);
            }
        }
        return data;
    }
    
    var djvu_threshold = function(smoothness, maxBlockSize, minBlockSize, blockFactor) {
        if (!smoothness)
            smoothness = 0.2;
        if (!maxBlockSize)
            maxBlockSize = 64;
        if (!minBlockSize)
            minBlockSize = 32;
        if (!blockFactor)
            blockFactor = 2;
            
        var canvas = document.getElementById("image-preview");
        var context = canvas.getContext("2d");    
        var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        var data = new IData(imageData.data, canvas.width, canvas.height);
        
        var histogram = [];
        for (var i = 0; i < 256; i++) {
            histogram[i] = 0;
        }
        var maxColour = new PixelRGB(0, 0, 0);
        var maxCount = 0;
        for (var y = 0; y < canvas.height; y++) {
            for (var x = 0; x < canvas.width; x++) {
                var currentPixel = data.getPixelRGB(x, y);
                var approxColour = (((currentPixel.r & 0xfc) << 10) |
                                    ((currentPixel.g & 0xfc) << 4)  |
                                    ((currentPixel.b & 0xfc) >> 2));
                var count = histogram[approxColour]++;
                if (count > maxCount) {
                    maxCount = count;
                    maxColour = new PixelRGB((currentPixel.r & 0xfc),
                                             (currentPixel.g & 0xfc),
                                             (currentPixel.b & 0xfc));
                }
            }
        }
        if (maxColour.r < 128 || maxColour.g < 128 || maxColour.b < 128)
            maxColour = new PixelRGB(255, 255, 255);
        
        var fData = djvu_threshold_h(data, smoothness, maxBlockSize, minBlockSize, blockFactor, new PixelRGB(0, 0, 0), maxColour);
        context.putImageData(imageData, 0, 0);
    }
    
    $('#binarise-form').submit(function () {
        //$('#threshold-input').val(defThresh);
    });
    
    
});

