(function ($) {
    "use strict";
    //Setup
    $(document).ready(function() {
        var gB = 1;
        var gC = 1;
        //Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
        var rScale = 0.2989;
        var gScale = 0.5870;
        var bScale = 0.1140;
        var imageObj = new Image();
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
        
            $("#bslider").slider("value", gB);
            $("#cslider").slider("value", gC);
            $("#bslider").width(imageObj.width * 2);
            $("#cslider").width(imageObj.width * 2);
        };
    
        imageObj.src = $("#image-thumb").attr("src");
    
        function blend(data, colour, factor) {
            var i;
            if (factor <= 0) {
                for (i = 0; i < data.length; i += 4) {
                    data[i] = colour;
                    data[i+1] = colour;
                    data[i+2] = colour;
                }
            } else if (factor < 1) {
                for (i = 0; i < data.length; i += 4) {
                    data[i] = colour + factor * (data[i] - colour);
                    data[i+1] = colour + factor * (data[i+1] - colour);
                    data[i+2] = colour + factor * (data[i+2] - colour);
                }
            } else if (factor > 1) {
                for (i = 0; i < data.length; i += 4) {
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
    
        function averageShade(data) {
            var histo = [];
            var i;
            for (i = 0; i < 256; i++) {
                histo[i] = 0;
            }
            for (i = 0; i < data.length; i += 4) {
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
    
        function bcProcess() {
            var canvasV = document.getElementById("image-preview");
            var contextV = canvasV.getContext("2d");
            var canvasO = document.getElementById("image-original");
            var contextO = canvasO.getContext("2d");
        
            var imageData = contextO.getImageData(0, 0, canvasV.width, canvasV.height);
            var data = imageData.data;
            blend(data, 0, gB);
            blend(data, averageShade(data), gC);
            contextV.putImageData(imageData, 0, 0);
        }
    
        $("#bslider").slider({
                            animate: true,
                            min: 0,
                            max: 5,
                            orientation: "horizontal",
                            step: 0.025,
                            value: gB,
                            range: false,
                            slide: function(event, ui) {
                                gB = ui.value;
                                bcProcess();
                            }
        });

        $("#cslider").slider({
                            animate: true,
                            min: 0,
                            max: 5,
                            orientation: "horizontal",
                            step: 0.025,
                            value: gC,
                            range: false,
                            slide: function(event, ui) {
                                gC = ui.value;
                                bcProcess();
                            }
        });
    });
})(jQuery)
