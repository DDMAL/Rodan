(function ($) {
    "use strict";
    $(document).ready(function() {
        // Kinetic Stage
        var stage;
    
        // Image Object
        var imageObj = new Image();
    
        //Fraction of image width to make the margin
        var marginWidth = 0.05;

        // Vertical padding for the polygons
        var polyPadding = 2;

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
    
        function selectPoly(poly) {
            if (selectedPoly !== null && selectedPoly !== poly) {
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
    

        function findNearestPoints(point) 
        {
            var minDist = -1;
            var minGroup = null;
            var minPoint = null;
            var minNeighbour = null;
            var gPoint = null;
            var poly = null;
            var nPoints = null;
            var dist = null;
            for(var i = 0; i < stage.get(".group").length; i++)
            {
                if(stage.get(".group")[i] !== undefined)
                {
                    var group = stage.get(".group")[i];
                    gPoint = $.extend({}, true, point);
                    gPoint.x -= group.getX();
                    gPoint.y -= group.getY();
                    poly = group.get(".poly")[0];
                    for (var j = 0; j < poly.getPoints().length; j++)
                    {
                        var anchor = group.attrs.anchors[j];
                        var dY = anchor.getY() - gPoint.y;
                        dist = Math.abs(dY);
                        if (minDist < 0 || dist < minDist) {
                            minDist = dist;
                            minGroup = group;
                        }
                    }
                }
            }
        
            minDist = -1;
            gPoint = $.extend({}, true, point);
            gPoint.x -= minGroup.getX();
            gPoint.y -= minGroup.getY();
            poly = minGroup.get(".poly")[0];
            nPoints = poly.getPoints().length;
            for (i = 0; i < nPoints; i++) {
                var A = minGroup.attrs.anchors[i];
                var B = null;
                if (i === (nPoints - 1)) {
                    B = minGroup.attrs.anchors[0];
                } else {
                    B = minGroup.attrs.anchors[i + 1];
                }
                var APx = gPoint.x - A.getX();
                var APy = gPoint.y - A.getY();
            
                var ABx = B.getX() - A.getX();
                var ABy = B.getY() - A.getY();
            
                var AB2 = (ABx * ABx) + (ABy * ABy);
                var ABAP = (APx * ABx) + (APy * ABy);
                var t = ABAP / AB2;
                if (t < 0) {
                    t = 0;
                } else if (t > 1) {
                    t = 1;
                }
                var Cx = A.getX() + (ABx * t);
                var Cy = A.getY() + (ABy * t);
                var Dx = Cx - gPoint.x;
                var Dy = Cy - gPoint.y;
                dist = Math.sqrt((Dx * Dx) + (Dy * Dy));
                if (minDist < 0 || dist < minDist) {
                    minDist = dist;
                    minPoint = A;
                    minNeighbour = B;
                }
            }
            return [minPoint, minNeighbour];
        }
        
        function flattenPoints(points) {
            var fPoints = [];
            var p;
            for (p in points) {
                if (points[p] !== undefined) {
                    var point = points[p];
                    fPoints.push(point.x);
                    fPoints.push(point.y);
                }
            }
            return fPoints;
        }
        
        function selectAnchors(anchors) {
            var a, anchor;
            for (a in selectedPoints) {
                if (selectedPoints[a] !== undefined) {
                    anchor = selectedPoints[a];
                    anchor.attrs.fill = '#ddd'; 
                }
            }
            for (a in anchors) {
                if (anchors[a] !== undefined) {
                    anchor = anchors[a];
                    anchor.attrs.fill = 'red';
                    anchor.getLayer().draw();
                }
            }
            selectedPoints = anchors;
        }
        
        function addAnchor(group, x, y) {
            var layer = group.getLayer();

            var anchor = new Kinetic.Circle({
                x: x,
                y: y,
                stroke: '#666',
                fill: '#ddd',
                strokeWidth: 1,
                radius: 3,
                draggable: true,
                dragBoundFunc: function(pos) {
                    var newX = pos.x < margin ? margin : pos.x;
                    newX = newX > (margin + imageObj.width) ? (margin + imageObj.width) : newX;
                    var newY = pos.y < margin ? margin : pos.y;
                    newY = newY > (margin + imageObj.height) ? (margin + imageObj.height) : newY;
                    return {
                        x: newX,
                        y: newY
                    };
                }
            });
            anchor.on("dragmove", function() {
                var poly = group.get(".poly")[0];
                var anchorI = group.attrs.anchors.indexOf(anchor);
                var pA = group.attrs.anchors[anchorI];
                var pointA = poly.attrs.points[anchorI];
                var nPoints = poly.attrs.points.length;
                pointA.y = pA.getY();
                pointA.x = pA.getX();
                layer.draw();
            });
            anchor.on("mousedown touchstart", function() {
                group.setDraggable(false);
                selectAnchors([this]);
                layer.draw();
            });
            anchor.on("dragend", function() {
                var poly = group.get(".poly")[0];
                var minX = poly.attrs.points[0].x;
                var minY = poly.attrs.points[0].y;
                var maxX = 0;
                var maxY = 0;
                var p;
                for (p in poly.getPoints()) {
                    if (poly.getPoints()[p] !== undefined) {
                        var point = poly.getPoints()[p];
                        minX = Math.min(minX, point.x);
                        minY = Math.min(minY, point.y);
                        maxX = Math.max(maxX, point.x);
                        maxY = Math.max(maxY, point.y);
                    }
                }
                group.setDragBoundFunc(function(pos) {
                    var newX = pos.x < (margin - minX) ? (margin - minX) : pos.x;
                    newX = newX > (margin + imageObj.width) ? (margin + imageObj.width) : newX;
                    var newY = pos.y < (margin + imageObj.width - maxX) ? (margin + imageObj.width - maxX) : pos.y;
                    newY = newY > (margin + imageObj.height - maxY) ? (margin + imageObj.height - maxY) : newY;
                    return {
                        x: newX,
                        y: newY
                    };
                });
                poly.attrs.width = maxX - minX;
                poly.attrs.height = maxY - minY;
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
            group.attrs.anchors.push(anchor);
            group.add(anchor);
        }
        
        function removePoly(poly) {
            var group, layer;
            if (poly === undefined) {
                var i;
                for (i = stage.get(".group").length - 1; i >= 0; i--) {
                    group = stage.get(".group")[i];
                    var gPoly = group.get(".poly")[0];
                    if (gPoly.attrs.fill === pSelColour) {
                        layer = group.getLayer();
                        layer.remove(group);
                        layer.destroy();
                        break;
                    }
                }
            } else {
                group = poly.getParent();
                layer = group.getLayer();
                layer.remove(group);
                layer.destroy();
            }
            selectedPoly = null;
        }

        function addPoint(e) {
            var point = {x: e.layerX, y: e.layerY};
            var nearestPoints = findNearestPoints(point);
            var group = nearestPoints[0].getParent();
            var poly = group.get(".poly")[0];
            var i0 = group.attrs.anchors.indexOf(nearestPoints[0]);
            var i1 = group.attrs.anchors.indexOf(nearestPoints[1]);
            var highPos = Math.max(i0, i1);
            point.x -= group.getX();
            point.y -= group.getY();
            if (Math.abs(i0 - i1) > 1) {
                poly.attrs.points.push(point);
            } else {
                poly.attrs.points.splice(highPos, 0, point);
            }
            var newPoly = addPoly(poly.getPoints(), group.getX(), group.getY());
            removePoly(poly);
            selectPoly(newPoly);
        }
        
        function deselectPoints() {
            var a;
            for (a in selectedPoints) {
                if (selectedPoints[a] !== undefined) {
                    var anchor = selectedPoints[a];
                    anchor.attrs.fill = '#ddd';
                    anchor.getLayer().draw();
                }
            }
            selectedPoints = [];
        }
        
        function addPoly(points, x, y, sel) {
            
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
                var canvas = document.getElementById("image-preview");
                if (($(window).scrollTop() - 40) > canvas.offsetTop) {
                    y += ($(window).scrollTop() - 40) - canvas.offsetTop;
                }
            }
            //Find maxima and minima
            var minX = points[0];
            var minY = points[1];
            var maxX = 0;
            var maxY = 0;
            var i;
            for (i = 2; (i + 1) < points.length; i += 2) {
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
                dragBoundFunc: function(pos) 
                {
                    var newX = pos.x < (margin - minX) ? (margin - minX) : pos.x;
                    newX = newX > (margin + imageObj.width - maxX) ? (margin + imageObj.width - maxX) : newX;
                    var newY = pos.y < (margin - minY) ? (margin - minY) : pos.y;
                    newY = newY > (margin + imageObj.height - maxY) ? (margin + imageObj.height - maxY) : newY;
                    return {
                        x: newX,
                        y: newY
                    };
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
                opacity: 0.2,
                name: "poly"
            });
            group.add(poly);
            var p;
            for (p in poly.getPoints()) {
                if (poly.getPoints()[p] !== undefined) {
                    var point = poly.getPoints()[p];
                    addAnchor(group, point.x, point.y);
                }
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
            });
        
            layer.draw();
            return poly;
        }
        
        function findContainedPoints(box) {
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
            for(var i = 0; i < stage.get(".group").length; i++)
            {
                if (stage.get(".group")[i] !== undefined)
                {
                    var group = stage.get(".group")[i];
                    for(var j = 0; j < group.attrs.anchors.length; j++)
                    {
                        if (group.attrs.anchors[j] !== undefined)
                        {
                            var anchor = group.attrs.anchors[j];
                            var adjX = anchor.getX() + group.getX() - margin;
                            var adjY = anchor.getY() + group.getY() - margin;
                            if (adjX >= tLX && adjY >= tLY && adjX <= bRX && adjY <= bRY)
                            {
                                sPoints.push(anchor);
                            }
                        }
                    }
                }
            }
            return sPoints;
        }
        
        function polyToRect(points) {
            if (points[0] instanceof Object) {
                points = flattenPoints(points);
            }
            var nPoints = [];
            nPoints[0] = points[0];
            nPoints[1] = points[1];
            var i;
            for (i = 2; i < 8; i++) {
                nPoints[i] = 0;
            }
            for (i = 2; (i + 1) < points.length; i += 2) {
                nPoints[0] = Math.min(nPoints[0], points[i]);
                nPoints[1] = Math.min(nPoints[1], points[i + 1]);
                nPoints[4] = Math.max(nPoints[4], points[i]);
                nPoints[5] = Math.max(nPoints[5], points[i + 1]);
            }
            nPoints[1] -= polyPadding;
            nPoints[5] += polyPadding;
            nPoints[2] = nPoints[4];
            nPoints[3] = nPoints[1];
            nPoints[6] = nPoints[0];
            nPoints[7] = nPoints[5];
            return nPoints;
        }
    
        function makeRect(points) {
            var nPoints;
            if (!points) {
                var i;
                for (i = stage.get(".group").length - 1; i >= 0; i--) {
                    var group = stage.get(".group")[i];
                    var poly = group.get(".poly")[0];
                    if (poly.attrs.fill === pSelColour) {
                        nPoints = polyToRect(poly.attrs.points);
                        addPoly(nPoints, group.getX(), group.getY());
                        var layer = group.getLayer();
                        layer.remove(group);
                        stage.remove(layer);
                        break;
                    }
                }
            } else {
                nPoints = polyToRect(points);
                addPoly(nPoints);
            }
        }
    
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
                 //   var boxStart = stage.getUserPosition(e);
                    selectionBox = new Kinetic.Rect({
                        x: e.layerX,//boxStart.x,
                        y: e.layerY,//boxStart.y,
                        width: 0,
                        height: 0,
                        fill: 'yellow',
                        opacity: 0.2,
                        stroke: 'black',
                        strokewidth: 3,
                        visible: false
                    });
                    var layer = new Kinetic.Layer();
                    layer.add(selectionBox);
                    stage.add(layer);
                    layer.draw();
                    var dStage = document.getElementById("image-preview");//stage.getDOM();
                    var bodyDOM = document.getElementsByTagName("body")[0];
                    var moveListener = function(e) {
                        if (selectionBox !== null) {
                            if (!selectionBox.isVisible()) {
                                selectionBox.attrs.visible = true;
                            }
                            var dX = e.layerX - selectionBox.getX();
                            var dY = e.layerY - selectionBox.getY();
                            selectionBox.setAttrs({
                                width: dX,
                                height: dY
                            });
                            selectionBox.getLayer().draw();
                        }
                    };
                    var upListener = function() {
                        if (selectionBox !== null) {
                            selectAnchors(findContainedPoints(selectionBox));
                            layer = selectionBox.getLayer();
                            layer.remove(selectionBox);
                            layer.draw();
                            layer.destroy();
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
            var i, j;
            for (i = 0; i < sPoints.length; i++) {
                polys[i] = [];
                for (j = 0; j < sPoints[i].length; j++) {
                    polys[i].push(sPoints[i][j][0] * scaleVal);
                    polys[i].push(sPoints[i][j][1] * scaleVal);
                }
                makeRect(polys[i]);
            }
        };
        imageObj.src = $("#image-original").attr("src");
    
        function deletePoints() {
            var changedPolys = [];
            var s, p, poly, group;
            for (s in selectedPoints) {
                if (selectedPoints[s] !== undefined) {
                    var sPoint = selectedPoints[s];
                    group = sPoint.getParent();
                    poly = group.get(".poly")[0];
                    if (changedPolys.indexOf(poly) === -1) {
                        changedPolys.push(poly);
                    }
                    var pI = group.attrs.anchors.indexOf(sPoint);
                    group.attrs.anchors.splice(pI, 1);
                    poly.attrs.points.splice(pI, 1);
                }
            }
            for (p in changedPolys) {
                if (changedPolys[p] !== undefined) {
                    poly = changedPolys[p];
                    group = poly.getParent();
                    if (poly.getPoints().length > 1) {
                        addPoly(poly.getPoints(), group.getX(), group.getY());
                    }
                    removePoly(poly);
                }
            }
        }
    
        $("#addPoly").bind('click', function() {addPoly();});
        $("#removePoly").bind('click', function() {removePoly();});
        $('body').keydown(function(e) {
            if (e.which === 8 || e.which === 46) {
                e.preventDefault();
                if (selectedPoints.length === 0) {
                    removePoly();
                } else {
                    deletePoints();
                }
            }
        });
    
    
        $('#form').submit(function () {
            $('#JSON-input').val(function() {
                var staves = stage.get(".group");
                var oCoords = [];
                var i, j;
                for (i = staves.length - 1; i >= 0; i--) {
                    var group = staves[i];
                    var poly = group.get(".poly")[0];
                    oCoords[i] = [];
                    for (j in poly.attrs.points) {
                        if (poly.attrs.points[j] !== undefined) {
                            oCoords[i][j] = [];
                            var point = poly.attrs.points[j];
                            oCoords[i][j][0] = Math.round((point.x + group.getX() - margin) / scaleVal);
                            oCoords[i][j][1] = Math.round((point.y + group.getY() - margin) / scaleVal);
                        }
                    }
                }
                return JSON.stringify(oCoords);
            });
        });
    });
})(jQuery)
