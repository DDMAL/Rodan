(function ($) {
    //Setup
    $(document).ready(function () {
        "use strict";
        var imageObj;
        var stage;
        var defRulerWidth = 100;
        var defRulerHeight = 4;
        var rulerShow = true;
        var rulerHoriz = true;
        var defAngle = 0;

        function toggleRuler() {
            var ruler = stage.get(".ruler")[0];
            if (rulerShow) {
                rulerShow = false;
                ruler.hide();
            } else {
                rulerShow = true;
                ruler.show();
            }
            ruler.getLayer().draw();
        }

        function reorientRuler() {
            var ruler = stage.get(".ruler")[0];
            if (rulerHoriz) {
                rulerHoriz = false;
                ruler.setWidth(defRulerHeight);
                ruler.setHeight(defRulerWidth);
                ruler.setDragBoundFunc(function(pos) {
                    return {
                        x: pos.x,
                        y: 0
                    };
                });
            } else {
                rulerHoriz = true;
                ruler.setWidth(defRulerWidth);
                ruler.setHeight(defRulerHeight);
                ruler.setDragBoundFunc(function(pos) {
                    return {
                        x: 0,
                        y: pos.y
                    };
                });
            }
            var rX = ruler.getX();
            ruler.setX(ruler.getY());
            ruler.setY(rX)
            ruler.getLayer().draw();
        }
        
        $(document).on('click', '#toggleRuler', toggleRuler);
        $(document).on('click', '#reorientRuler', reorientRuler);

        function rotate(angle) {
            defAngle = angle;
            var image = stage.get(".image")[0];
            image.setRotationDeg(angle);
            image.getLayer().draw();
        }

        //Setup
        window.onload = function() {
            imageObj = new Image();
            imageObj.onload = function() {
                var dist = Math.ceil(Math.sqrt(Math.pow(imageObj.width, 2) + Math.pow(imageObj.height, 2)));
                stage = new Kinetic.Stage({
                    container: "image-preview",
                    width: dist,
                    height: dist,
                    stroke: 'black',
                    strokewidth: 2
                });
                var layer = new Kinetic.Layer();
                var image = new Kinetic.Image({
                    x: dist / 2,
                    y: dist / 2,
                    width: imageObj.width,
                    height: imageObj.height,
                    offset: [imageObj.width / 2, imageObj.height / 2],
                    image: imageObj,
                    name: "image"
                });
                layer.add(image);
                stage.add(layer);

                var rulerOffset = dist / 10;
                defRulerWidth = dist;
                var rLayer = new Kinetic.Layer();
                var ruler = new Kinetic.Rect({
                    x: 0,
                    y: rulerOffset,
                    width: defRulerWidth,
                    height: defRulerHeight,
                    fill: 'black',
                    draggable: true,
                    dragBoundFunc: function(pos) {
                        return {
                            x: 0,
                            y: pos.y
                        };
                    },
                    name: "ruler"
                });
                rLayer.add(ruler);
                stage.add(rLayer);
                //toggleRuler();
                rotate(0);
            };
    
            //Image path (TO BE REPLACED LATER)
            imageObj.src = $("#image-original").attr("src");
    
            //jQuery slider definition for threshold controller
            $(".knob").knob({
    		    'value':defAngle,
    		    'width': 100,
    			'min':0,
    			'max':360,
    			'displayPrevious':true,
    			'change':function(v, ipt) {
    			    rotate(v);
    			}
    		});
            $('#form').submit(function () {
                var outAngle = (defAngle > 180) ? (defAngle - 360) : defAngle;
                $('#angle-input').val(outAngle);
            });
        };
    });
})(jQuery)
