(function ($) {
    "use strict";
    //Default threshold before user input
    //Maximum value for greyness
    //Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
    var defColour = "blue";
    var imageObj;
    var stage;

    //Fraction of image width to make the margin
    var marginWidth = 0.05;

    // Pixel margin size
    var margin = 0;
    
    function update(group, activeAnchor) {
        var topLeft = group.get(".topLeft")[0];
        var topRight = group.get(".topRight")[0];
        var bottomRight = group.get(".bottomRight")[0];
        var bottomLeft = group.get(".bottomLeft")[0];
        var rect = group.get(".rect")[0];

        // update anchor positions
        switch (activeAnchor.getName()) {
          case "topLeft":
            topRight.attrs.y = activeAnchor.attrs.y;
            bottomLeft.attrs.x = activeAnchor.attrs.x;
            break;
          case "topRight":
            topLeft.attrs.y = activeAnchor.attrs.y;
            bottomRight.attrs.x = activeAnchor.attrs.x;
            break;
          case "bottomRight":
            bottomLeft.attrs.y = activeAnchor.attrs.y;
            topRight.attrs.x = activeAnchor.attrs.x;
            break;
          case "bottomLeft":
            bottomRight.attrs.y = activeAnchor.attrs.y;
            topLeft.attrs.x = activeAnchor.attrs.x;
            break;
        }

        rect.setPosition(topLeft.attrs.x, topLeft.attrs.y);
        rect.setSize(topRight.attrs.x - topLeft.attrs.x, bottomLeft.attrs.y - topLeft.attrs.y);
    }

    function addAnchor(group, x, y, name) {
        var stage = group.getStage();
        var layer = group.getLayer();
    
        var anchor = new Kinetic.Circle({
            x: x,
            y: y,
            stroke: '#666',
            fill: '#ddd',
            strokeWidth: 1,
            radius: 3,
            name: name,
            draggable: true,
            dragBounds: {
                top: margin,
                left: margin,
                right: margin + imageObj.width,
                bottom: margin + imageObj.height
            }
        });
    
        anchor.on("dragmove", function() {
            update(group, this);
            layer.draw();
        });
        anchor.on("mousedown touchstart", function() {
            group.setDraggable(false);
            layer.draw();
        });
        anchor.on("dragend", function() {
            var rect = group.get(".rect")[0];
            group.setDragBounds({
                top: margin - rect.getY(),
                left: margin - rect.getX(),
                right: margin + imageObj.width - (rect.getX() + rect.getWidth()),
                bottom: margin + imageObj.height - (rect.getY() + rect.getHeight())
            });
            group.setDraggable(true);
            layer.draw();
        });
        anchor.on("mouseover", function() {
            var layer = this.getLayer();
            document.body.style.cursor = "pointer";
            this.setStrokeWidth(3);
            layer.draw();
        });
        anchor.on("mouseout", function() {
            var layer = this.getLayer();
            document.body.style.cursor = "default";
            this.setStrokeWidth(1);
            layer.draw();
        });
    
        group.add(anchor);
    }

    function makeRect() {
        var group = new Kinetic.Group({
            x: 0,
            y: 0,
            draggable: true,
            name: "box"
        });
    
        var layer = new Kinetic.Layer();
    
        layer.add(group);
        stage.add(layer);
    
        var rect = new Kinetic.Rect({
            x: (imageObj.width / 20.0) + margin,
            y: (imageObj.height / 20.0) + margin,
            width: 18.0 * (imageObj.width / 20.0),
            height: 18.0 * (imageObj.height / 20.0),
            fill: defColour,
            stroke: 'black',
            strokeWidth: 2,
            alpha: 0.2,
            name: "rect"
        });
        group.setDragBounds({
            top: margin - rect.getY(),
            left: margin - rect.getX(),
            right: margin + imageObj.width - (rect.getX() + rect.getWidth()),
            bottom: margin + imageObj.height - (rect.getY() + rect.getHeight())
        });
        group.add(rect);

        addAnchor(group, rect.getX(), rect.getY(), "topLeft");
        addAnchor(group, rect.getX() + rect.getWidth(), rect.getY(), "topRight");
        addAnchor(group, rect.getX() + rect.getWidth(), rect.getY() + rect.getHeight(), "bottomRight");
        addAnchor(group, rect.getX(), rect.getY() + rect.getHeight(), "bottomLeft");
    
        stage.draw();
    }
    
    function logRect() {
        var group = stage.get(".box")[0];
        var topLeft = group.get(".topLeft")[0];
        var bottomRight = group.get(".bottomRight")[0];
        var oCoords = [];
        oCoords[0] = Math.round(topLeft.getX() + group.getX() - margin);
        oCoords[1] = Math.round(topLeft.getY() + group.getY() - margin);
        oCoords[2] = Math.round(bottomRight.getX() + group.getX() - margin);
        oCoords[3] = Math.round(bottomRight.getY() + group.getY() - margin);
        return oCoords;
    }

    //Setup
    $(document).ready(function() {
        imageObj = new Image();
        //Calculate initial threshold with the Brink formula and draw binarized image
        imageObj.onload = function () {
            margin = imageObj.width * marginWidth;
            stage = new Kinetic.Stage({
                container: "image-preview",
                width: imageObj.width + (2 * margin),
                height: imageObj.height + (2 * margin)
            });
            var layer = new Kinetic.Layer();
            var image = new Kinetic.Image({
                x: margin,
                y: margin,
                width: imageObj.width,
                height: imageObj.height,
                image: imageObj,
                stroke: 'black',
                strokewidth: 2
            });

            layer.add(image);
            stage.add(layer);

            makeRect();
        };
    
        //Image path (TO BE REPLACED LATER)
        imageObj.src = $("#image-original").attr("src");
    
        $('#form').submit(function () {
            var points = logRect();
            $('#tlx-input').val(points[0]);
            $('#tly-input').val(points[1]);
            $('#brx-input').val(points[2]);
            $('#bry-input').val(points[3]);
            $('#imw-input').val(imageObj.width);
        });
    });
})(jQuery)
