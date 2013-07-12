(function ($)
{
    var RKSegment = function(element, options)
    {
        var defaults = {
            image: null,  // the image object we're segmenting
            polyPoints: null,   // the polygon points we're applying to the image
            originalWidth: null,
            anchorSize: 7
        };

        var settings = $.extend({}, defaults, options);

        var globals = {
            kStage: null,   // kinetic stuff
            kImageLayer: null,
            kImage: null,
            imageObject: null,
            scalingFactor: null,
            scaledMargin: null,
            marginWidth: 0.05,
            selectedPoly: null,
            unselectedColour: "blue",
            selectedColour: "red",
            selectedAnchor: null
        };
        $.extend(settings, globals);

        var self = this;  // global class reference is `self`

        var init = function ()
        {
            $('body').keydown(function(event)
            {
                // handle events: delete (8, 46, 68), transform (82), new polygon (78)
                if (event.which === 8 || event.which === 46 || event.which === 68)
                {
                    event.preventDefault();

                    if (settings.selectedPoly && settings.selectedAnchor === null)
                    {
                        _deletePoly(settings.selectedPoly);
                    }
                    else if (settings.selectedAnchor !== null)
                    {
                        _deleteAnchor();
                    }
                    return false;
                }
                else if (event.which === 82)
                {
                    event.preventDefault();
                    if (settings.selectedPoly)
                    {
                        _transformPolygonToRectagle(settings.selectedPoly);
                    }
                    return false;
                }
                else if (event.which === 78)
                {
                    event.preventDefault();
                    if (!settings.selectedPoly)
                    {
                        self.createPolygon();
                    }
                }
            });

            settings.imageObject = new Image();
            settings.imageObject.onload = function()
            {
                settings.scalingFactor = settings.imageObject.width / settings.originalWidth;
                settings.scaledMargin = settings.imageObject.width * settings.marginWidth;

                settings.kStage = new Kinetic.Stage({
                    container: settings.parentObject.getAttribute('id'),
                    width: settings.imageObject.width,
                    height: settings.imageObject.height,
                    margin: settings.scaledMargin
                });

                settings.kImageLayer = _createImageLayer();

                settings.kImage = new Kinetic.Image({
                    width: settings.imageObject.width,
                    height: settings.imageObject.height,
                    image: settings.imageObject
                });

                settings.kImageLayer.add(settings.kImage);
                settings.kStage.add(settings.kImageLayer);

                var i = settings.polyPoints.length;

                while (i--)
                {
                    var polys = [],
                        j = settings.polyPoints[i].length;

                    while (j--)
                    {
                        var x = settings.polyPoints[i][j][0] * settings.scalingFactor,
                            y = settings.polyPoints[i][j][1] * settings.scalingFactor;
                        polys.push([x, y]);
                    }

                    var group = _createGroup(),
                        layer = new Kinetic.Layer(),
                        poly = _createPolygon(polys, group);

                    layer.add(group);
                    settings.kStage.add(layer);

                    layer.draw();
                }
            };

            // this triggers the image onload method.
            settings.imageObject.src = settings.image;
        };

        init();  // call init when the object is created.

        var _createImageLayer = function()
        {
            var layer = new Kinetic.Layer();

            /*
                We detect a click on the image layer and do the OUTSIDE anchor adding. The polygon handler
                handles clicks INSIDE.
            */
            layer.on("mousedown", function(event)
            {
                if (event.altKey && settings.selectedPoly !== null)
                {
                    // Override default.
                    event.preventDefault();

                    /*
                        If the group has been moved from it's default starting position,
                        it will have x,y values that represent the offset from its starting
                        which we need to take into account when clicking; otherwise we
                        simply use the mouse event position.
                    */
                    var group = settings.selectedPoly.parent,
                        groupAnchors = group.attrs.anchors,
                        offsetX = (group.attrs.x) ? Math.abs(event.layerX - group.attrs.x) : event.layerX,
                        offsetY = (group.attrs.y) ? Math.abs(event.layerY - group.attrs.y) : event.layerY,
                        hitPoint = {x: offsetX, y: offsetY},
                        indices = _getIndicesOfNeighbourAnchorsForNewAnchor(groupAnchors, hitPoint, "outside");

                    _addAnchor(offsetX, offsetY, group, indices[1]);

                    return false;
                }
                else if (!event.altKey && settings.selectedPoly !== null)
                {
                    // de-select the currently selected polygon by clicking outside of the poly.
                    _deselectPoly(settings.selectedPoly);
                }
            }, false);

            return layer;
        };

        var _dragBoundFunc = function(pos)
        {
            return {x: pos.x, y: pos.y};
        };

        var _setAnchorHandlers = function(anchor, group)
        {
            anchor.on("dragmove", function(event) {
                var poly = group.get(".poly")[0],
                    anchorIdx = group.attrs.anchors.indexOf(anchor),
                    thisAnchor = group.attrs.anchors[anchorIdx],
                    polyPoint = poly.attrs.points[anchorIdx];

                polyPoint.y = this.getY();
                polyPoint.x = this.getX();
                group.getLayer().draw();
            });

            anchor.on("mousedown", function(event)
            {
                _selectAnchor(this, event);
            });
        };

        var _createGroup = function()
        {
            var group = new Kinetic.Group({
                draggable: true,
                name: 'group',
                dragBoundFunc: _dragBoundFunc,
                anchors: []
            });

            group.on("mousedown", function(event)
            {
                var poly = group.get(".poly")[0];
                _selectPoly(poly);
            }, false);

            return group;
        };

        var _createPolygon = function(polys, group)
        {
            var poly = new Kinetic.Polygon({
                points: polys,
                fill: settings.unselectedColour,
                stroke: 'black',
                opacity: 0.2,
                strokeWidth: 2,
                name: "poly"
            });
            group.add(poly);

            poly.on("mousedown", function(event)
            {
                /*
                    Detect clicks *inside* the polygon.
                */
                if (event.altKey && settings.selectedPoly !== null)
                {
                    event.preventDefault();

                    // Go through all the line segments.
                    var group = this.parent,
                        groupAnchors = group.attrs.anchors,
                        offsetX = (group.attrs.x) ? Math.abs(event.layerX - group.attrs.x) : event.layerX,
                        offsetY = (group.attrs.y) ? Math.abs(event.layerY - group.attrs.y) : event.layerY,
                        hitPoint = {x: offsetX, y: offsetY},
                        indices = _getIndicesOfNeighbourAnchorsForNewAnchor(groupAnchors, hitPoint, "inside");

                    _addAnchor(offsetX, offsetY, group, indices[1]);

                    return false;
                }

            }, false);

            var j = 0,
                polyLength = polys.length;

            while (j < polyLength)
            {
                var x = polys[j][0],
                    y = polys[j][1],
                    anchor = _createAnchor(x, y);

                group.add(anchor);
                group.attrs.anchors.push(anchor);
                _setAnchorHandlers(anchor, group);
                ++j;
            }

            return poly;
        };

        var _selectPoly = function(poly)
        {
            if (settings.selectedPoly === poly)
                return;

            if (settings.selectedPoly !== null && settings.selectedPoly !== poly)
            {
                settings.selectedPoly.setFill(settings.unselectedColour);
                settings.selectedPoly.getLayer().draw();
                settings.selectedPoly = null;
            }

            settings.selectedPoly = poly;
            settings.selectedPoly.setFill(settings.selectedColour);
            settings.selectedPoly.getLayer().draw();
        };

        var _deselectPoly = function(poly)
        {
            if (settings.selectedPoly !== null)
            {
                settings.selectedPoly.setFill(settings.unselectedColour);
                settings.selectedPoly.getLayer().draw();
                settings.selectedPoly = null;
            }

            if (settings.selectedAnchor !== null)
            {
                _deselectAnchor();
            }
        }

        var _deletePoly = function(poly)
        {
            var group = poly.getParent(),
                layer = group.getLayer();

            layer.remove(group);
            layer.destroy();

            settings.selectedPoly = null;
        };

        var _createAnchor = function(x, y)
        {
            var anchor = new Kinetic.Circle({
                x: x,
                y: y,
                fill: "#ddd",
                strokeWidth: 2,
                radius: settings.anchorSize,
                draggable: true,
                dragBoundFunc: _dragBoundFunc
            });

            return anchor;
        };

        var _addAnchor = function(x, y, group, index)
        {
            var poly = group.get(".poly")[0],
                anchor = _createAnchor(x, y),
                pointObj = {"x": x, "y": y};

            group.add(anchor);
            group.attrs.anchors.splice(index, 0, anchor);
            poly.attrs.points.splice(index, 0, pointObj);

            _setAnchorHandlers(anchor, group);
            group.getLayer().draw();
        };

        var _selectAnchor = function(anchor)
        {
            if (settings.selectedAnchor === anchor)
                return;

            _deselectAnchor();

            settings.selectedAnchor = anchor;
            settings.selectedAnchor.setStroke(settings.selectedColour);

            settings.selectedAnchor.getLayer().draw();
        };

        /*
            Deselects the currently selected anchor.
        */
        var _deselectAnchor = function()
        {
            if (settings.selectedAnchor !== null)
            {
                settings.selectedAnchor.setStroke("black");
                settings.selectedAnchor.getLayer().draw();
                settings.selectedAnchor = null;
            }
        }

        /*
            Deletes the currently selected anchor.
        */
        var _deleteAnchor = function()
        {
            if (settings.selectedAnchor !== null)
            {
                var group = settings.selectedAnchor.getParent(),
                    poly = group.get(".poly")[0],
                    anchorIdx = group.attrs.anchors.indexOf(settings.selectedAnchor);

                var rem = group.attrs.anchors.splice(anchorIdx, 1),
                    remp = poly.attrs.points.splice(anchorIdx, 1);

                _deselectAnchor();
                settings.selectedAnchor = null;

                rem[0].remove();
                group.getLayer().clear();
                group.getLayer().draw();
            }
        }

        /**
         * This contains a collection of geometrical functions intended to help Kinetic.
         */
        var _getDistanceToLine = function(aLinePointA, aLinePointB, aPoint)
        {
            if(aLinePointA.x == aLinePointB.x)
            {
                return Math.abs(aLinePointA.y - aLinePointB.y);
            }
            var slope = (aLinePointA.y - aLinePointB.y) / (aLinePointA.x - aLinePointB.x),
                xIntercept = aLinePointA.y - (slope * aLinePointA.x),
                distance = ((slope * aPoint.x) - aPoint.y + xIntercept) / Math.sqrt((slope * slope) + 1);

            return Math.abs(distance);
        };

        var _getOrthogonalIntersectOfPointToLine = function(aLinePointA, aLinePointB, aPoint)
        {
            if(aLinePointA.x == aLinePointB.x)
            {
                return {x: aLinePointA.x, y: aPoint.y};
            }
            var slope = (aLinePointA.y - aLinePointB.y) / (aLinePointA.x - aLinePointB.x),
                xIntercept = aLinePointA.y - (slope * aLinePointA.x),
                orthogonalSlope = -1 / slope,
                orthogonalXIntercept = aPoint.y - (orthogonalSlope * aPoint.x),
                interceptionX = (orthogonalXIntercept - xIntercept) / (slope - orthogonalSlope),
                interceptionY = (slope * interceptionX) + xIntercept;

            return {x: interceptionX, y: interceptionY};
        };

        var _isIntegerBetweenOthers = function(aInt0, aInt1, aTest)
        {
            if ((aInt0 <= aInt1 && aInt0 <= aTest && aTest<= aInt1) || (aInt0 >= aInt1 && aInt0 >= aTest && aTest>= aInt1))
            {
                return true;
            }
            return false;
        };

        var _getClosestPoint = function(aPointA, aPointB, aOriginPoint)
        {
            var distanceASquared = Math.pow(aPointA.x - aOriginPoint.x, 2) + Math.pow(aPointA.y - aOriginPoint.y, 2);
            var distanceBSquared = Math.pow(aPointB.x - aOriginPoint.x, 2) + Math.pow(aPointB.y - aOriginPoint.y, 2);
            if (distanceASquared <= distanceBSquared)
            {
                return aPointA;
            }
            return aPointB;
        };

        var _getDistanceToPoint = function(aPointA, aPointB)
        {
            var distanceSquared = Math.pow(aPointA.x - aPointB.x, 2) + Math.pow(aPointA.y - aPointB.y, 2);
            return Math.sqrt(distanceSquared);
        };

        var _isPointInLineSegmentPlane = function(aLinePointA, aLinePointB, aPoint)
        {
            var result = {isInPlane: false, distanceToPlane: -1, distanceToLineSegment: -1};
            var orthogonalLineIntersectionOfPointToLine = _getOrthogonalIntersectOfPointToLine(aLinePointA, aLinePointB, aPoint);
            result.isInPlane = _isIntegerBetweenOthers(aLinePointA.x, aLinePointB.x, orthogonalLineIntersectionOfPointToLine.x);
            if (result.isInPlane)
            {
                result.distanceToLineSegment = _getDistanceToLine(aLinePointA, aLinePointB, aPoint);
                result.distanceToPlane = 0;
            }
            else
            {
                var closestPoint = _getClosestPoint(aLinePointA, aLinePointB, aPoint);
                result.distanceToPlane = _getDistanceToPoint(closestPoint, orthogonalLineIntersectionOfPointToLine);
                result.distanceToLineSegment = _getDistanceToPoint(closestPoint, aPoint);
            }
            return result;
        };

        /**
         * Given a group and a point, returns the indecies that should neighbour the new anchor.
         * aPosition is either "inside" the polygon or "outside".
         */
        var _getIndicesOfNeighbourAnchorsForNewAnchor = function(aGroupAnchors, aPoint, aPosition)
        {
            var numberOfPoints = aGroupAnchors.length;
            var resultArray = [];
            var bestIndex = -1;
            for (var i = 0; i < numberOfPoints; i++)
            {
                // Get points of line segment (note: we set y to neg. so as to resemble pure Cart. coords.)
                var nextIndex = (i + 1) % numberOfPoints;
                var pointA = aGroupAnchors[i].getAbsolutePosition();
                var pointB = aGroupAnchors[nextIndex].getAbsolutePosition();
                pointA.y *= -1;
                pointB.y *= -1;
                var testPoint = {x: aPoint.x, y: aPoint.y * -1};

                // Determine if the point is in the line segment plane.
                resultArray[i] = _isPointInLineSegmentPlane(pointA, pointB, testPoint);

                // If this is the first, mark it.  Else, figure out if this line segment is the new best.
                var bestResult = resultArray[bestIndex];
                var currentResult = resultArray[i];

                if (bestIndex < 0)
                    bestIndex = i;
                else if (aPosition === "outside")
                {
                    if (Math.round(bestResult.distanceToLineSegment) == Math.round(currentResult.distanceToLineSegment))
                        bestIndex = bestResult.distanceToPlane <= currentResult.distanceToPlane ? bestIndex : i;
                    else if (bestResult.isInPlane && currentResult.isInPlane)
                        bestIndex = bestResult.distanceToLineSegment <= currentResult.distanceToLineSegment ? bestIndex : i;
                    else
                        bestIndex = bestResult.distanceToLineSegment <= currentResult.distanceToLineSegment ? bestIndex : i;
                }
                else if (aPosition === "inside")
                {
                    if (!bestResult.isInPlane && currentResult.isInPlane)
                        bestIndex = i;
                    else if (bestResult.isInPlane && currentResult.isInPlane)
                        bestIndex = bestResult.distanceToLineSegment <= currentResult.distanceToLineSegment ? bestIndex : i;
                }
            }

            return [bestIndex, (bestIndex + 1) % numberOfPoints];
        };

        var _transformPolygonToRectagle = function(aPolygon)
        {
            if(aPolygon === null)
            {
                return;
            }

            var group = aPolygon.parent,
                groupAnchors = group.attrs.anchors;
            if(groupAnchors.length <= 4)
            {
                return;
            }

            _deselectAnchor();
            _deselectPoly(aPolygon);

            // Get boundries.
            var xMinimum = groupAnchors[0].getAbsolutePosition().x,
                xMaximum = groupAnchors[0].getAbsolutePosition().x,
                yMinimum = groupAnchors[0].getAbsolutePosition().y,
                yMaximum = groupAnchors[0].getAbsolutePosition().y;
            for (var i = 1; i < groupAnchors.length; i++)
            {
                var point = groupAnchors[i].getAbsolutePosition();
                xMinimum = point.x < xMinimum ? point.x : xMinimum;
                xMaximum = point.x > xMaximum ? point.x : xMaximum;
                yMinimum = point.y < yMinimum ? point.y : yMinimum;
                yMaximum = point.y > yMaximum ? point.y : yMaximum;
            }

            // Make new poly.
            var points = [[xMinimum, yMaximum], [xMaximum, yMaximum], [xMaximum, yMinimum], [xMinimum, yMinimum]];
            _deletePoly(aPolygon);
            self.createPolygon(points);
        };

        // PUBLIC METHODS \\
        this.getPolyPoints = function() {
            // if the stage isn't ready, we can't get the polys
            if (settings.kStage === null)
            {
                return;
            }

            var staves = settings.kStage.get('.group'),
                segments = [],
                i = staves.length;

            while (i--)
            {
                var group = staves[i],
                    poly = group.get(".poly")[0],
                    points = poly.attrs.points,
                    numPoly = poly.attrs.points.length;

                segments[i] = [];

                for (var j = 0; j < numPoly; ++j)
                {
                    if (points[j] !== undefined)
                    {
                        var point = points[j];
                        segments[i][j] = [];
                        segments[i][j][0] = Math.round((point.x + group.getX() - settings.marginWidth) / settings.scalingFactor);
                        segments[i][j][1] = Math.round((point.y + group.getY() - settings.marginWidth) / settings.scalingFactor);
                    }
                }
            }

            return segments;
        };

        this.createPolygon = function(points)
        {
            points = (typeof points !== "undefined") ? points : [[10, 10], [100, 10], [100, 100], [10, 100]];  // create a new polygon if points is undefined

            var group = _createGroup(),
                layer = new Kinetic.Layer(),
                polygon = _createPolygon(points, group);

            layer.add(group);
            settings.kStage.add(layer);

            layer.draw();
        };
    };

    $.fn.RKSegment = function(options)
    {
        return this.each(function ()
        {
            var element = $(this);

            // return early if this element already has a plugin instance
            if (element.data('RKSegment'))
                return;

            options.parentObject = element[0];

            var seg = new RKSegment(this, options);
            element.data('RKSegment', seg);
        });
    };
})(jQuery);