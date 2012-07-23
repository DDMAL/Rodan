(function ($) {
    "use strict";
    //Setup
    $(document).ready(function() {
        var gBrightness = 1;
        var gContrast = 1;
        var gColour = 1;
        var ordering = 0;
        //Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
        var rScale = 0.2989;
        var gScale = 0.5870;
        var bScale = 0.1140;
        var imageObj = new Image();
            
        var averageColour, gImage;
        
        function greyscale(data) {
            var dLen = data.length;
            var gData = [];
            var i, brightness;
            for (i = 0; i < dLen; i += 4) {
                brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
                gData[i] = brightness;
                gData[i+1] = brightness;
                gData[i+2] = brightness;
                gData[i+3] = 255;
            }
            return gData;
        }
        
        function averageShade(data) {
            var dLen = data.length;
            var histo = [];
            var i;
            for (i = 0; i < 256; i++) {
                histo[i] = 0;
            }
            for (i = 0; i < dLen; i += 4) {
                var brightness = rScale * data[i] + gScale * data[i + 1] + bScale * data[i + 2];
                histo[Math.round(brightness)]++;
            }
            var pSum = 0;
            var hSum = 0;
            for (i = 0; i < 256; i++) {
                hSum += histo[i];
                pSum += (i * histo[i]);
            }
            return pSum / hSum;
        }
        
        imageObj.onload = function() {
            //Adjust size of canvas to fit image
            var canvasV = document.getElementById("image-preview");
            var contextV = canvasV.getContext("2d");
            var canvasO = document.getElementById("image-original");
            var contextO = canvasO.getContext("2d");
        
            canvasV.width = imageObj.width;
            canvasV.height = imageObj.height;
            canvasO.width = imageObj.width;
            canvasO.height = imageObj.height;
        
            contextV.drawImage(imageObj, 0, 0, canvasV.width, canvasV.height, 0, 0, canvasV.width, canvasV.height);
            contextO.drawImage(imageObj, 0, 0, canvasO.width, canvasO.height, 0, 0, canvasO.width, canvasO.height);
            
            $("#brightness-slider").slider("value", gBrightness);
            $("#contrast-slider").slider("value", gContrast);
            $("#colour-slider").slider("value", gColour);
            $("#brightness-slider").width(imageObj.width * 2);
            $("#contrast-slider").width(imageObj.width * 2);
            $("#colour-slider").width(imageObj.width * 2);
            
            var imageData = contextO.getImageData(0, 0, canvasV.width, canvasV.height);
            var data = imageData.data;
            averageColour = averageShade(data);
            gImage = greyscale(data);
        };
    
        imageObj.src = $("#image-thumb").attr("src");

        function blendColour(data, colour, factor) {
            var dLen = data.length;
            var i;
            if (factor <= 0) {
                for (i = 0; i < dLen; i += 4) {
                    data[i] = colour;
                    data[i+1] = colour;
                    data[i+2] = colour;
                }
            } else if (factor < 1) {
                for (i = 0; i < dLen; i += 4) {
                    data[i] = colour + factor * (data[i] - colour);
                    data[i+1] = colour + factor * (data[i+1] - colour);
                    data[i+2] = colour + factor * (data[i+2] - colour);
                }
            } else if (factor > 1) {
                for (i = 0; i < dLen; i += 4) {
                    data[i] = colour + factor * (data[i] - colour);
                    data[i+1] = colour + factor * (data[i+1] - colour);
                    data[i+2] = colour + factor * (data[i+2] - colour);
                    if (data[i] > 255) {
                        data[i] = 255;
                    } else if (data[i] < 0) {
                        data[i] = 0;
                    }
                    if (data[i+1] > 255) {
                        data[i+1] = 255;
                    } else if (data[i+1] < 0) {
                        data[i+1] = 0;
                    }
                    if (data[i+1] > 255) {
                        data[i+1] = 255;
                    } else if (data[i+2]< 0) {
                        data[i+2] = 0;
                    }
                }
            }
        }

        function blendImage(data1, data2, factor) {
            var dLen = data1.length;
            if (dLen !== data2.length) {
                return;
            }
            var i;
            if (factor <= 0) {
                for (i = 0; i < dLen; i += 4) {
                    data1[i] = data2[i];
                    data1[i+1] = data2[i+1];
                    data1[i+2] = data2[i+2];
                }
            } else if (factor < 1) {
                for (i = 0; i < dLen; i += 4) {
                    data1[i] = data2[i] + factor * (data1[i] - data2[i]);
                    data1[i+1] = data2[i+1] + factor * (data1[i+1] - data2[i+1]);
                    data1[i+2] = data2[i+2] + factor * (data1[i+2] - data2[i+2]);
                }
            } else if (factor > 1) {
                for (i = 0; i < dLen; i += 4) {
                    data1[i] = data2[i] + factor * (data1[i] - data2[i]);
                    data1[i+1] = data2[i+1] + factor * (data1[i+1] - data2[i+1]);
                    data1[i+2] = data2[i+2] + factor * (data1[i+2] - data2[i+2]);
                    if (data1[i] > 255) {
                        data1[i] = 255;
                    } else if (data1[i] < 0) {
                        data1[i] = 0;
                    }
                    if (data1[i+1] > 255) {
                        data1[i+1] = 255;
                    } else if (data1[i+1] < 0) {
                        data1[i+1] = 0;
                    }
                    if (data1[i+1] > 255) {
                        data1[i+1] = 255;
                    } else if (data1[i+2]< 0) {
                        data1[i+2] = 0;
                    }
                }
            }
        }
    
        function bcProcess() {
            var canvasV = document.getElementById("image-preview");
            var contextV = canvasV.getContext("2d");
            var canvasO = document.getElementById("image-original");
            var contextO = canvasO.getContext("2d");
        
            var imageData = contextO.getImageData(0, 0, canvasV.width, canvasV.height);
            var data = imageData.data;
            if (ordering === 0) {
                blendColour(data, 0, gBrightness);
                blendColour(data, averageShade(data), gContrast);
                blendImage(data, greyscale(data), gColour);
            } else if (ordering === 1) {
                blendColour(data, 0, gBrightness);
                blendImage(data, greyscale(data), gColour);
                blendColour(data, averageShade(data), gContrast);
            } else if (ordering === 2) {
                blendColour(data, averageColour, gContrast);
                blendColour(data, 0, gBrightness);
                blendImage(data, greyscale(data), gColour);
            } else if (ordering === 3) {
                blendColour(data, averageColour, gContrast);
                blendImage(data, greyscale(data), gColour);
                blendColour(data, 0, gBrightness);
            } else if (ordering === 4) {
                blendImage(data, gImage, gColour);
                blendColour(data, 0, gBrightness);
                blendColour(data, averageShade(data), gContrast);
            } else {
                blendImage(data, gImage, gColour);
                blendColour(data, averageShade(data), gContrast);
                blendColour(data, 0, gBrightness);
            }
            contextV.putImageData(imageData, 0, 0);
        }
        
        $("#ordering").change(function() {
            ordering = $("#ordering option:selected").attr("value");
            bcProcess();
        });
    
        $("#brightness-slider").slider({
                            animate: true,
                            min: 0,
                            max: 5,
                            orientation: "horizontal",
                            step: 0.025,
                            value: gBrightness,
                            range: false,
                            slide: function(event, ui) {
                                gBrightness = ui.value;
                                bcProcess();
                            }
        });

        $("#contrast-slider").slider({
                            animate: true,
                            min: 0,
                            max: 5,
                            orientation: "horizontal",
                            step: 0.025,
                            value: gContrast,
                            range: false,
                            slide: function(event, ui) {
                                gContrast = ui.value;
                                bcProcess();
                            }
        });
        
        $("#colour-slider").slider({
                            animate: true,
                            min: 0,
                            max: 5,
                            orientation: "horizontal",
                            step: 0.025,
                            value: gColour,
                            range: false,
                            slide: function(event, ui) {
                                gColour = ui.value;
                                bcProcess();
                            }
        });
    });
})(jQuery)
