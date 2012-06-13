//Default threshold before user input
//Maximum value for greyness
//Scale values for grayscaling RGB (taken from http://www.mathworks.com/help/toolbox/images/ref/rgb2gray.html )
var widthLim = 750;
var heightLim = 750;
defBoxX = 10;
defBoxY = 10;
defBoxW = 100;
defBoxH = 50;
defColour = "blue"
defSelColour = "red"
var deletionMode = false;
var imageObj;
var stage;

function IData(data) {
    this.data = data;
    this.getPoint = function(x, y) {
        var convX = x * 4;
        var convY = y * imageObj.width * 4;
        return this.data[convX + convY];
    };
    this.setPoint = function(x, y, val) {
        var convX = x * 4;
        var convY = y * imageObj.width * 4;
        this.data[convX + convY] = val;
        this.data[convX + convY + 1] = val;
        this.data[convX + convY + 2] = val;
    };
    this.isBlack = function(x, y) {
        return this.getPoint(x, y) === BLACK;
    };
    this.isFail = function(x, y) {
        return this.getPoint(x, y) === FAIL;
    };
}

//Setup
$(document).ready(function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = initImage;
    
    //Image path (TO BE REPLACED LATER)
    imageObj.src = "/static/images/mhd.jpg";
    
    
});

initImage = function() {
    if (imageObj.width > widthLim || imageObj.height > heightLim) {
        var scaleValX = 0;
        var scaleValY = 0;
        scaleValX = widthLim / imageObj.width;
        scaleValY = heightLim / imageObj.height;
        var scaleVal = Math.min(scaleValX, scaleValY);
        imageObj.height *= scaleVal;
        imageObj.width *= scaleVal;
    }
    
    stage = new Kinetic.Stage({
        container: "container",
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
    
    image.on("mousedown", function() {
        resetColours();
    });
    addPoly([0, 0, 100, 0, 200, 0, 200, 100, 100, 100, 0, 100]);
}

addPoly = function(points, x, y, sel) {
    var undef = false;
    if (!points) {
        points = [0, 0, 100, 0, 100, 50, 0, 50];
    }
    if (!x) {
        x = 10 + defBoxX;
        undef = true;
    }
    if (!y) {
        y = 10 + defBoxY;
        undef = true;
    }
    var group = new Kinetic.Group({
        x: x,
        y: y,
        draggable: true,
        name: "staff"
    });
    
    var layer = new Kinetic.Layer();
    
    layer.add(group);
    stage.add(layer);
    
    var poly = new Kinetic.Polygon({
        points: points,
        fill: sel ? defSelColour : defColour,
        stroke: 'black',
        strokeWidth: 2,
        alpha: .2,
        name: "poly"
    });
    group.add(poly);
    
    for (var i in poly.attrs.points) {
        var point = poly.attrs.points[i];
        addAnchor(group, point.x, point.y, i);
    }
    group.on("dragstart", function() {
        this.moveToTop();
    });
    group.on("mousedown touchstart", function() {
        resetColours();
        poly.attrs.fill = defSelColour;
        layer.draw();
    });
    
    if (undef) {
        defBoxX += 10;
        defBoxY += 10;
    }
    
    stage.draw();
}

update = function(group, activeAnchor) {
    var poly = group.get(".poly")[0];
    var anchorI = activeAnchor.getName();
    var pA = group.get("." + anchorI)[0];
    var pointA = poly.attrs.points[anchorI];
    var nPoints = poly.attrs.points.length;
    var internal = true;
    if (anchorI == 0
        || anchorI == ((nPoints / 2) - 1)
        || anchorI == (nPoints / 2)
        || anchorI == (nPoints - 1)) {
        internal = false;
    }
    if (internal) {
        var pointB, pB;
        for (var i in poly.attrs.points) {
            var pointT = poly.attrs.points[i];
            if (pointT.x == pointA.x && pointT !== pointA) {
                pointB = pointT;
                pB = group.get("." + i)[0];
                pointB.x = pA.attrs.x;
                pB.attrs.x = pA.attrs.x;
            }
        }
    }
    pointA.y = pA.attrs.y;
    pointA.x = pA.attrs.x;
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

addLeftEnd = function() {
    var lX = 50;
    
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        var layer = group.getLayer();
        var poly = group.get(".poly")[0];
        if (poly.attrs.fill == defSelColour) {
            var pLen = poly.attrs.points.length;
            var fP = poly.attrs.points[0];
            var lP = poly.attrs.points[pLen - 1];
            var minX = Math.min(fP.x, lP.x);
            
            var newPoints = new Array();
            newPoints.push(minX - lX);
            newPoints.push(fP.y);
            for (var j in poly.attrs.points) {
                var point = poly.attrs.points[j];
                if (j == 0 || j == (pLen - 1)) {
                    newPoints.push(minX);
                } else {
                    newPoints.push(point.x);
                }
                newPoints.push(point.y);
            }
            newPoints.push(minX - lX);
            newPoints.push(lP.y);
            
            var nX = group.attrs.x;
            var nY = group.attrs.y;
            
            layer.remove(group);
            stage.remove(layer);
            addPoly(newPoints, nX, nY, true);
            
            break;
        }
    }
}

addRightEnd = function() {
    var rX = 50;
    
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        var layer = group.getLayer();
        var poly = group.get(".poly")[0];
        if (poly.attrs.fill == defSelColour) {
            var pLen = poly.attrs.points.length;
            var fPI = (pLen / 2) - 1;
            var lPI = pLen / 2;
            var fP = poly.attrs.points[fPI];
            var lP = poly.attrs.points[lPI];
            var maxX = Math.max(fP.x, lP.x);
            
            var newPoints = new Array();
            
            for (var j in poly.attrs.points) {
                var point = poly.attrs.points[j];
                if (j == fPI) {
                    newPoints.push(maxX);
                    newPoints.push(point.y);
                    newPoints.push(maxX + rX);
                    newPoints.push(point.y);
                } else if (j == lPI) {
                    newPoints.push(maxX + rX);
                    newPoints.push(point.y);
                    newPoints.push(maxX);
                    newPoints.push(point.y);
                } else {
                    newPoints.push(point.x);
                    newPoints.push(point.y);
                }
            }
            
            var nX = group.attrs.x;
            var nY = group.attrs.y;
            
            layer.remove(group);
            stage.remove(layer);
            addPoly(newPoints, nX, nY, true);
            
            break;
        }
    }
}

removeLeftEnd = function() {
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        var layer = group.getLayer();
        var poly = group.get(".poly")[0];
        if (poly.attrs.fill == defSelColour && poly.attrs.points.length > 4) {
            var pLen = poly.attrs.points.length;
            
            var newPoints = new Array();
            for (var j = 1; j < (pLen - 1); j++) {
                var point = poly.attrs.points[j];
                newPoints.push(point.x);
                newPoints.push(point.y);
            }
            
            var nX = group.attrs.x;
            var nY = group.attrs.y;
            
            layer.remove(group);
            stage.remove(layer);
            addPoly(newPoints, nX, nY, true);
            
            break;
        }
    }
}

removeRightEnd = function() {
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        var layer = group.getLayer();
        var poly = group.get(".poly")[0];
        if (poly.attrs.fill == defSelColour && poly.attrs.points.length > 4) {
            var pLen = poly.attrs.points.length;
            var fPI = (pLen / 2) - 1;
            var lPI = pLen / 2;
            
            var newPoints = new Array();
            for (var j = 0; j < pLen; j++) {
                var point = poly.attrs.points[j];
                if (j != fPI && j != lPI) {
                    newPoints.push(point.x);
                    newPoints.push(point.y);
                }
            }
            
            var nX = group.attrs.x;
            var nY = group.attrs.y;
            
            layer.remove(group);
            stage.remove(layer);
            addPoly(newPoints, nX, nY, true);
            
            break;
        }
    }
}

resetColours = function(colour) {
    if (!colour) {
        colour = defColour;
    }
    for (var i = stage.get(".poly").length - 1; i >= 0; i--) {
        var poly = stage.get(".poly")[i];
        poly.attrs.fill = colour;
        poly.getLayer().draw();
    }
}

removePoly = function() {
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        var poly = group.get(".poly")[0];
        if (poly.attrs.fill == defSelColour) {
            layer = group.getLayer();
            layer.remove(poly);
            stage.remove(layer);
        }
    }
}

logPolys = function() {
    for (var i = stage.get(".staff").length - 1; i >= 0; i--) {
        var group = stage.get(".staff")[i];
        if (group.get(".poly").length > 0) {
            var poly = group.get(".poly")[0];
            var oCoords = "";
            for (var j in poly.attrs.points) {
                var point = poly.attrs.points[j];
                oCoords += " (" + point.x + ", " + point.y + ")";
            }
            console.log("Bounding Points:" + oCoords);
        }
    }
}

maskImage = function() {
    for (var i = stage.get(".box").length - 1; i >= 0; i--) {
        var box = stage.get(".box")[i];
        if (box.get(".rect").length > 0) {
            var rect = box.get(".rect")[0];
            var x1 = box.attrs.x;
            var y1 = box.attrs.y;
            var x2 = box.attrs.x + rect.attrs.width;
            var y2 = box.attrs.y + rect.attrs.height;
            
        }
    }
}