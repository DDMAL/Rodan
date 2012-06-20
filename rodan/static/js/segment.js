$(document).ready(function() {
    // Kinetic Stage
    var stage;
    
    // Image Object
    var imageObj = new Image();
    
    //Fraction of image width to make the margin
    var marginWidth = 0.05;
    
    // Pixel margin size
    var margin = 0;
    
    //Scale factor for scaled image
    var scaleVal = 1;
    
    //Default polygon colour
    var pDefColour = 'blue';
    
    //Selected polygon colour
    var pSelColour = 'red';
    
    //Currently selected polygon
    var selectedPoly = null;
    
    var selectedPoints = [];
    
    var selectionBox = null;    
    
    imageObj.onload = function () {
        // Scaling factors and page margins
        var oWidth = $("#width").text();
        scaleVal = imageObj.width / oWidth;
        margin = imageObj.width * marginWidth;
        
        stage = new Kinetic.Stage({
            container: "image-preview",
            width: imageObj.width + (margin * 2),
            height: imageObj.height + (margin * 2),
            margin: margin
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
        
        image.on("mousedown touchstart", function(e) {
            selectPoly();
            if(e.shiftKey) {
                addPoint(e);
            } else {
                deselectPoints();
                // CREATE DRAG BOX
                var boxStart = stage.getUserPosition(e);
                selectionBox = new Kinetic.Rect({
                    x: boxStart.x,
                    y: boxStart.y,
                    width: 0,
                    height: 0,
                    fill: 'yellow',
                    alpha: 0.2,
                    stroke: 'black',
                    strokewidth: 3,
                    visible: false
                });
                var layer = new Kinetic.Layer();
                layer.add(selectionBox);
                stage.add(layer);
                layer.draw();
                var dStage = stage.getDOM();
                var bodyDOM = document.getElementsByTagName("body")[0];
                var moveListener = function(e) {
                    if (selectionBox != null) {
                        var point = stage.getUserPosition(e);
                        if (!selectionBox.isVisible()) {
                            selectionBox.attrs.visible = true;
                        }
                        dX = point.x - selectionBox.getX();
                        dY = point.y - selectionBox.getY();
                        selectionBox.setAttrs({
                            width: dX,
                            height: dY
                        });
                        selectionBox.getLayer().draw();
                    }
                };
                var upListener = function() {
                    if (selectionBox != null) {
                        selectAnchors(findContainedPoints(selectionBox));
                        
                        layer = selectionBox.getLayer();
                        layer.remove(selectionBox);
                        layer.draw();
                        stage.remove(layer);
                        selectionBox = null;
                        bodyDOM.removeEventListener("mouseup", upListener);
                    }
                };
                dStage.addEventListener("mousemove", moveListener, true);
                bodyDOM.addEventListener("mouseup", upListener, true);
            }
        });
        var sPoints = JSON.parse($("#JSON").text());
        var polys = [];
        for (var i = 0; i < sPoints.length; i++) {
            polys[i] = [];
            for (var j = 0; j < sPoints[i].length; j++) {
                polys[i].push(sPoints[i][j][0] * scaleVal);
                polys[i].push(sPoints[i][j][1] * scaleVal);
            }
            addPoly(polys[i]);
        }
    }
    imageObj.src = $("#image-original").attr("src");
    
    var addPoly = function(points, x, y, sel) {
        //Default poly
        if (!points) {
            points = [0,                   0,
                      imageObj.width / 20, 0,
                      imageObj.width / 20, imageObj.height / 40,
                      0,                   imageObj.height / 40];
        } else if (points[0] instanceof Object) {
            points = flattenPoints(points);
        }
        if (!x) {
            x = margin;
        }
        if (!y) {
            y = margin;
        }
        //Find maxima and minima
        var minX = points[0];
        var minY = points[1];
        var maxX = 0;
        var maxY = 0;
        for (var i = 2; (i + 1) < points.length; i += 2) {
            minX = Math.min(minX, points[i]);
            minY = Math.min(minY, points[i + 1]);
            maxX = Math.max(maxX, points[i]);
            maxY = Math.max(maxY, points[i + 1]);
        }
        //Group containing polygon and points
        var group = new Kinetic.Group({
            x: x,
            y: y,
            draggable: true,
            name: "group",
            dragBounds: {
                top: margin - minY,
                left: margin - minX,
                right: margin + imageObj.width - maxX,
                bottom: margin + imageObj.height - maxY
            },
            anchors: []
        });
        var layer = new Kinetic.Layer();
        layer.add(group);
        stage.add(layer);

        var poly = new Kinetic.Polygon({
            points: points,
            fill: sel ? pSelColour : pDefColour,
            stroke: 'black',
            strokeWidth: 2,
            alpha: .2,
            name: "poly"
        });

        group.add(poly);
        
        for each (point in poly.getPoints()) {
            addAnchor(group, point.x, point.y);
        }
        group.on("dragstart", function() {
            this.moveToTop();
        });
        
        group.on("mousedown touchstart", function(e) {
            selectPoly(poly);
            if(e.shiftKey) {
                addPoint(e);
            }
        });
        
        poly.on("mousedown", function() {
            deselectPoints();
        })
        
        layer.draw();
        return poly;
    }
    
    var removePoly = function(poly) {
        if (!poly) {
            for (var i = stage.get(".group").length - 1; i >= 0; i--) {
                var group = stage.get(".group")[i];
                var poly = group.get(".poly")[0];
                if (poly.attrs.fill == pSelColour) {
                    var layer = group.getLayer();
                    layer.remove(group);
                    stage.remove(layer);
                    break;
                }
            }
        } else {
            var group = poly.getParent();
            var layer = group.getLayer();
            layer.remove(group);
            stage.remove(layer);
        }
    }
    
    var addAnchor = function(group, x, y) {
        var layer = group.getLayer();

        var anchor = new Kinetic.Circle({
            x: x,
            y: y,
            stroke: '#666',
            fill: '#ddd',
            strokeWidth: 1,
            radius: 3,
            draggable: true,
            dragBounds: {
                top: margin,
                left: margin,
                right: margin + imageObj.width,
                bottom: margin + imageObj.height
            },
        });
        anchor.on("dragmove", function() {
            var poly = group.get(".poly")[0];
            var anchorI = group.attrs.anchors.indexOf(anchor);
            var pA = group.attrs.anchors[anchorI];
            var pointA = poly.attrs.points[anchorI];
            var nPoints = poly.attrs.points.length;
            pointA.y = pA.attrs.y;
            pointA.x = pA.attrs.x;
            layer.draw();
        });
        anchor.on("mousedown touchstart", function() {
            group.draggable(false);
            selectPoint(this);
            layer.draw();
        });
        anchor.on("dragend", function() {
            var poly = group.get(".poly")[0];
            var minX = poly.attrs.points[0].x;
            var minY = poly.attrs.points[0].y;
            var maxX = 0;
            var maxY = 0;
            for each (point in poly.attrs.points) {
                minX = Math.min(minX, point.x);
                minY = Math.min(minY, point.y);
                maxX = Math.max(maxX, point.x);
                maxY = Math.max(maxY, point.y);
            }
            group.setDragBounds({
                top: margin - minY,
                left: margin - minX,
                right: margin + imageObj.width + minX - maxX,
                bottom: margin + imageObj.height + minY - maxY
            });
            poly.attrs.width = maxX - minX;
            poly.attrs.height = maxY - minY;
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
        group.attrs.anchors.push(anchor);
        group.add(anchor);
    }
    
    var selectPoly = function(poly) {
        if (selectedPoly != null) {
            selectedPoly.attrs.fill = pDefColour;
            selectedPoly.getLayer().draw();
            selectedPoly = null;
        }
        if (poly) {
            poly.attrs.fill = pSelColour;
            selectedPoly = poly;
            poly.getLayer().draw();
        }
    }
        
    var findNearestPoints = function(point) {
        var minDist = -1;
        var minPoint = null;
        var minNeighbour = null;
        for each (group in stage.get(".group")) {
            var gPoint = $.extend({}, true, point);
            gPoint.x -= group.getX();
            gPoint.y -= group.getY();
            var poly = group.get(".poly")[0];
            var nPoints = poly.getPoints().length;
            for (var i = 0; i < nPoints; i++) {
                var anchor = group.attrs.anchors[i];
                var dX = anchor.getX() - gPoint.x;
                var dY = anchor.getY() - gPoint.y;
                var dist = Math.sqrt((dX * dX) + (dY * dY));
                if (minDist < 0 || dist < minDist) {
                    minDist = dist;
                    minPoint = anchor;
                    if (i == 0) {
                        minNeighbour = group.attrs.anchors[nPoints - 1];
                    } else {
                        minNeighbour = group.attrs.anchors[i - 1];
                    }
                    var dNX = minNeighbour.getX() - gPoint.x;
                    var dNY = minNeighbour.getY() - gPoint.y;
                    var nDist = Math.sqrt((dNX * dNX) + (dNY * dNY));
                    var minNeighbourB = null;
                    if (i == (nPoints - 1)) {
                        minNeighbourB = group.attrs.anchors[0];
                    } else {
                        minNeighbourB = group.attrs.anchors[i + 1];
                    }
                    dNX = minNeighbourB.getX() - gPoint.x;
                    dNY = minNeighbourB.getY() - gPoint.y;
                    var nDistB = Math.sqrt((dNX * dNX) + (dNY * dNY));
                    if (nDistB < nDist) {
                        minNeighbour = minNeighbourB;
                    }
                }
            }
        }
        return [minPoint, minNeighbour];
    }
    
    var findContainedPoints = function(box) {
        var tLX = 0;
        var tLY = 0;
        var bRX = 0;
        var bRY = 0;
        if (box.getWidth() > 0) {
            tLX = box.getX() - margin;
            bRX = tLX + box.getWidth();
        } else {
            tLX = box.getX() + box.getWidth() - margin;
            bRX = tLX - box.getWidth();
        }
        if (box.getHeight() > 0) {
            tLY = box.getY() - margin;
            bRY = tLY + box.getHeight();
        } else {
            tLY = box.getY() + box.getHeight() - margin;
            bRY = tLY - box.getHeight();
        }
        
        var sPoints = [];
        
        for each (group in stage.get(".group")) {
            for each (anchor in group.attrs.anchors) {
                if (anchor.getX() >= tLX && anchor.getY() >= tLY
                    && anchor.getX() <= bRX && anchor.getY() <= bRY) {
                    sPoints.push(anchor);
                }
            }
        }
        return sPoints;
    }
    
    var flattenPoints = function(points) {
        var fPoints = [];
        for each (point in points) {
            fPoints.push(point.x);
            fPoints.push(point.y);
        }
        return fPoints;
    }
    
    var addPoint = function(e) {
        var point = stage.getUserPosition(e);
        var nearestPoints = findNearestPoints(point);
        var group = nearestPoints[0].getParent();
        var poly = group.get(".poly")[0];
        var i0 = group.attrs.anchors.indexOf(nearestPoints[0]);
        var i1 = group.attrs.anchors.indexOf(nearestPoints[1]);
        var highPos = Math.max(i0, i1);
        point.x -= group.getX();
        point.y -= group.getY();
        poly.attrs.points.splice(highPos, 0, point);
        var newPoly = addPoly(poly.getPoints(), group.getX(), group.getY());
        removePoly(poly);
        selectPoly(newPoly);
    }
        
    var selectPoint = function(point) {
        for each (anchor in selectedPoints) {
            anchor.attrs.fill = '#ddd';
        }
        point.attrs.fill = 'red';
        selectedPoints = [point];
    }
    
    var selectAnchors = function(anchors) {
        for each (anchor in selectedPoints) {
            anchor.attrs.fill = '#ddd';
        }
        for each (anchor in anchors) {
            anchor.attrs.fill = 'red';
            anchor.getLayer().draw();
        }
        selectedPoints = anchors;
    }
    
    var deselectPoints = function() {
        for each (anchor in selectedPoints) {
            anchor.attrs.fill = '#ddd';
            anchor.getLayer().draw();
        }
        selectedPoints = [];
    }
    
    var deletePoints = function() {
        var changedPolys = []
        for each (sPoint in selectedPoints) {
            var group = sPoint.getParent();
            var poly = group.get(".poly")[0];
            if (changedPolys.indexOf(poly) == -1)
                changedPolys.push(poly);
            var pI = group.attrs.anchors.indexOf(sPoint);
            group.attrs.anchors.splice(pI, 1);
            poly.attrs.points.splice(pI, 1);
        }
        for each (poly in changedPolys) {
            var group = poly.getParent();
            if (poly.getPoints().length > 1)
                addPoly(poly.getPoints(), group.getX(), group.getY());
            removePoly(poly);
        }
    }
    
    $("#addPoly").bind('click', function() {addPoly();});
    $("#removePoly").bind('click', function() {removePoly();});
    $('body').keydown(function(e) {
        if (e.which == 8 || e.which == 46) {
            e.preventDefault();
            deletePoints();
        }
    });
    
    
    $('#segment-form').submit(function () {
        $('#JSON-input').val(function() {
            var staves = stage.get(".staff");
            var oCoords = [];
            for (var i = staves.length - 1; i >= 0; i--) {
                var group = staves[i];
                var poly = group.get(".poly")[0];
                oCoords[i] = [];
                for (var j in poly.attrs.points) {
                    oCoords[i][j] = [];
                    var point = poly.attrs.points[j];
                    oCoords[i][j][0] = Math.round((point.x + group.attrs.x) / scaleVal);
                    oCoords[i][j][1] = Math.round((point.y + group.attrs.y) / scaleVal);
                }
            }
            return JSON.stringify(oCoords);
        });
    });
});