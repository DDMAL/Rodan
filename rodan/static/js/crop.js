//Default threshold before user input
//Maximum value for greyness
//Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
defColour = "blue"
var imageObj;
var stage;

//Setup
$(document).ready(function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = initImage;
    
    //Image path (TO BE REPLACED LATER)
    imageObj.src = $("#image-original").attr("src");
    
    $('#crop-form').submit(function () {
        var points = logRect();
        $('#tlx-input').val(points[0]);
        $('#tly-input').val(points[1]);
        $('#brx-input').val(points[2]);
        $('#bry-input').val(points[3]);
        $('#imw-input').val(imageObj.width);
    });
});

initImage = function() {
    stage = new Kinetic.Stage({
        container: "image-preview",
        width: imageObj.width,
        height: imageObj.height
    });
    var layer = new Kinetic.Layer();
    var image = new Kinetic.Image({
        x: 0,
        y: 0,
        width: imageObj.width,
        height: imageObj.height,
        image: imageObj
    });
    
    layer.add(image);
    stage.add(layer);
    
    makeRect();
}

makeRect = function() {
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
        x: imageObj.width / 20.,
        y: imageObj.height / 20.,
        width: 18. * (imageObj.width / 20.),
        height: 18. * (imageObj.height / 20.),
        fill: defColour,
        stroke: 'black',
        strokeWidth: 2,
        alpha: .2,
        name: "rect"
    });
    group.add(rect);

    addAnchor(group, rect.attrs.x, rect.attrs.y, "topLeft");
    addAnchor(group, rect.attrs.x + rect.attrs.width, rect.attrs.y, "topRight");
    addAnchor(group, rect.attrs.x + rect.attrs.width, rect.attrs.y + rect.attrs.height, "bottomRight");
    addAnchor(group, rect.attrs.x, rect.attrs.y + rect.attrs.height, "bottomLeft");
    
    stage.draw();
}

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

addAnchor = function(group, x, y, name) {
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
        draggable: true
    });
    
    anchor.on("dragmove", function() {
        update(group, this);
        layer.draw();
    });
    anchor.on("mousedown touchstart", function() {
        group.draggable(false);
        layer.draw();
    });
    anchor.on("dragend", function() {
        group.draggable(true);
        layer.draw();
    })
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

logRect = function() {
    var group = stage.get(".box")[0];
    var topLeft = group.get(".topLeft")[0];
    var bottomRight = group.get(".bottomRight")[0];
    var oCoords = new Array(4);
    oCoords[0] = Math.round(topLeft.attrs.x + group.attrs.x);
    oCoords[1] = Math.round(topLeft.attrs.y + group.attrs.y);
    oCoords[2] = Math.round(bottomRight.attrs.x + group.attrs.x);
    oCoords[3] = Math.round(bottomRight.attrs.y + group.attrs.y);
    return oCoords;
}