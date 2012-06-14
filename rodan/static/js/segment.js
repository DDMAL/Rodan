defBoxX = 10;
defBoxY = 10;
defBoxW = 100;
defBoxH = 50;
defColour = "blue"
defSelColour = "red"
var jsonPath = "/static/json_in/imdata.json";
var imageObj;
var stage;
var sPoints;

//Setup
$(document).ready(function() {
    imageObj = new Image();
    //Calculate initial threshold with the Brink formula and draw binarized image
    imageObj.onload = initImage;
    
    //Image path (TO BE REPLACED LATER)
    imageObj.src = $("#image-original").attr("src");
    
    $('#segment-form').submit(function () {
        $('#JSON-input').val(logPolys());
        $('#imw-input').val(imageObj.width);
    });
});

initImage = function() {
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
    $.get(jsonPath, function(data) {
        sPoints = $(data);
        var polys = new Array(sPoints.length);
        for (var i = 0; i < sPoints.length; i++) {
            polys[i] = new Array();
            for (var j = 0; j < sPoints[i].length; j++) {
                polys[i].push(sPoints[i][j][0]);
                polys[i].push(sPoints[i][j][1]);
            }
            addPoly(polys[i], 0, 0);
        }
    });
}

addPoly = function(points, x, y, sel) {
    var undef = false;
    if (!points) {
        points = [0, 0, 100, 0, 100, 50, 0, 50];
    }
    if (x == undefined) {
        x = 10 + defBoxX;
        undef = true;
    }
    if (y == undefined) {
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
            layer.remove(group);
            stage.remove(layer);
        }
    } 
}

logPolys = function() {
    var staves = stage.get(".staff");
    var oCoords = new Array(staves.length);
    for (var i = staves.length - 1; i >= 0; i--) {
        var group = staves[i];
        var poly = group.get(".poly")[0];
        oCoords[i] = new Array(poly.attrs.points.length);
        for (var j in poly.attrs.points) {
            oCoords[i][j] = new Array(2);
            var point = poly.attrs.points[j];
            oCoords[i][j][0] = Math.round((point.x + group.attrs.x));
            oCoords[i][j][1] = Math.round((point.y + group.attrs.y));
        }
    }
    return JSON.stringify(oCoords);
}