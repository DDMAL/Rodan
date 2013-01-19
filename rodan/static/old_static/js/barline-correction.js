(function($) {
    "use strict";
    var BarlineCorrection = function(element, options)
    {
        var elem = $(element);
        var mei;
        var imageObj = new Image();
        var systems = [];
        var stage;
        
        var defaults = {
            iwidth: 1000,
            barmargin: 5,
            scaleval: 1,
            minbar: 1,
            textsize: 15,
            textpadding: 3,
            meipath: "",
            bgimgpath: "",
            origwidth: null,
            origheight: null
        };
        
        var settings = $.extend({}, defaults, options);
        
        var globals = {
            canvasid: "imview"
        };
        
        $.extend(settings, globals);
        
        /******************************
         *      PUBLIC FUNCTIONS      *
         ******************************/
        // placeholder

        /******************************
         *      PRIVATE FUNCTIONS     *
         ******************************/
        
        var init = function() {
            $.when(loadPage(),
                   handleBackgroundImage()
            ).then(loadSuccess,
                   function () {
                       console.log("Failure to load the mei file or background image");
                   }
            );
        };
        
        var loadMei = function() {
            var currSystem = new Kinetic.Group({
                x: 0,
                y: 0,
                width: 0,
                height: 0,
                name: "system",
                bars: []
            });
            systems.push(currSystem);
            var layer = new Kinetic.Layer();
            layer.add(currSystem);
            stage.add(layer);

            mei.find("section").children().each(function() {
                if ($(this).is("sb")) {
                    resizeSystem(currSystem);
                    currSystem = new Kinetic.Group({
                        x: 0,
                        y: 0,
                        width: 0,
                        height: 0,
                        name: "system",
                        bars: []
                    });
                    systems.push(currSystem);
                    layer = new Kinetic.Layer();
                    layer.add(currSystem);
                    stage.add(layer);
                } else {
                    var id = $(this).attr("xml\\:id");
                    var facs = $(this).attr("facs");
                    if (facs.charAt(0) === "#") {
                        facs = facs.substring(1);
                    }
                    var zone = mei.find('[xml\\:id="' + facs + '"]');
                    var ulX = zone.attr("ulx") * settings.scaleval;
                    var ulY = zone.attr("uly") * settings.scaleval;
                    var width = (zone.attr("lrx") * settings.scaleval) - ulX;
                    var height = (zone.attr("lry") * settings.scaleval) - ulY;

                    var staves = $(this).children();
                    var nStaves = staves.size();
                    var staffEnds = [];
                    var staffIdList = [];
                    var staffFacsList = [];
                    var currStaff = 1;
                    staves.each(function(staff) {
                        var staffId = $(this).attr("xml\\:id");
                        var staffFacs = $(this).attr("facs");
                        staffIdList.push(staffId);
                        staffFacsList.push(staffFacs);
                        if (staffFacs.charAt(0) === "#") {
                            staffFacs = staffFacs.substring(1);
                        }
                        var staffZone = mei.find('[xml\\:id="' + staffFacs + '"]');
                        staffEnds.push((staffZone.attr("uly") * settings.scaleval) - ulY);
                        staffEnds.push((staffZone.attr("lry") * settings.scaleval) - ulY);
                    });
                    staffEnds.sort(function(a,b){return a-b;});
                    staffEnds.splice(staffEnds.length - 1, 1);
                    staffEnds.splice(0, 1);
                    addBar(stage, currSystem, ulX, ulY, width, height, staffEnds, id, facs, staffIdList, staffFacsList, $(this).attr("n"));
                }
            });
            resizeSystem(currSystem);
            stage.draw();
        };
        
        // asynchronous function
        var loadPage = function() {
            var dfd = $.Deferred();
            console.log(settings.meipath);
            if (settings.meipath) {
                $.get(settings.meipath, function(data) {
                    console.log("loading MEI file ...");

                    // save mei data
                    var meiDoc = $.parseXML(data);
                    mei = $(meiDoc);
                    dfd.resolve();
                });
            }
            else {
                // immediately resolve
                dfd.resolve();
            }

            // return promise
            return dfd.promise();
        };
        
        // asynchronous function
        var handleBackgroundImage = function() {
            console.log("loading background image ...");
            var dfd = $.Deferred();
            if (settings.bgimgpath) {
                imageObj.onload = function() {
                    dfd.resolve();
                }
                imageObj.src = settings.bgimgpath;
            }
            else {
                // immediately resolve
                dfd.resolve();
            }

            // return promise
            return dfd.promise();
        };
        
        var loadSuccess = function() {
           settings.scaleval = settings.iwidth / settings.origwidth;
           
            stage = new Kinetic.Stage({
                container: settings.canvasid,
                width: imageObj.width,
                height: imageObj.height
            });

            var img = new Kinetic.Image({
                x: 0,
                y: 0,
                width: imageObj.width,
                height: imageObj.height,
                image: imageObj
            });

            var iLayer = new Kinetic.Layer();
            iLayer.add(img);
            stage.add(iLayer);
            console.log(imageObj);
            // Add new bar on shift-click
            img.on("click", function(e) {
                if (e.shiftKey) {
                    //Add new bar, 25x25, calculate system membership
                    var pos = stage.getMousePosition(e);
                    var nearSystem = findNearestSystemToPoint(pos.y);
                    var systemSize = nearSystem.attrs.bars.length;
                    var systemBar = nearSystem.attrs.bars[systemSize - 1];
                    var nHeight = systemBar.attrs.height;
                    var nWidth = systemBar.attrs.width / 2;
                    addBar(stage, nearSystem, pos.x, pos.y, nWidth, nHeight, getStaffLines(systemBar), 0);
                    resizeSystem(nearSystem);
                    updateNumbers();
                }
            });
            // Cursor styling reset
            img.on("mouseover", function() {
                document.body.style.cursor = "default";
            });
            
            if (mei) {
                loadMei();
            }
        };

        var pushChangeBar = function() {
            
        };

        var pushDeleteBar = function() {
            
        };

        var pushAddBar = function() {
            
        };

        var pushSplitBar = function() {
            
        };

        var update = function(group, activeAnchor) {
            var topLeft = group.get(".tl")[0];
            var topRight = group.get(".tr")[0];
            var lowerRight = group.get(".lr")[0];
            var lowerLeft = group.get(".ll")[0];
            var bar = group.get(".bar")[0];
            var iBox = group.get(".barbox")[0];
            var nStaves = group.attrs.bars.length;
            topLeft.attrs.visible = true;
            topRight.attrs.visible = true;
            lowerRight.attrs.visible = true;
            lowerLeft.attrs.visible = true;
            // update anchor positions
            switch (activeAnchor.getName()) {
                case "tl":
                    if (nStaves > 1) {
                        if (activeAnchor.attrs.y > group.attrs.lines[0].getY()) {
                            activeAnchor.attrs.y = group.attrs.lines[0].getY();
                        }
                        group.attrs.bars[0].setY(activeAnchor.attrs.y);
                        group.attrs.bars[0].setHeight(group.attrs.lines[0].getY() - activeAnchor.attrs.y);
                    } else if (activeAnchor.attrs.y > lowerLeft.attrs.y) {
                        activeAnchor.attrs.y = lowerLeft.attrs.y;
                    }
                    if (activeAnchor.attrs.x > topRight.attrs.x) {
                        activeAnchor.attrs.x = topRight.attrs.x;
                    }
                    topRight.attrs.y = activeAnchor.attrs.y;
                    lowerLeft.attrs.x = activeAnchor.attrs.x;
                    break;
                case "tr":
                    if (nStaves > 1) {
                        if (activeAnchor.attrs.y > group.attrs.lines[0].getY()) {
                            activeAnchor.attrs.y = group.attrs.lines[0].getY();
                        }
                        group.attrs.bars[0].setY(activeAnchor.attrs.y);
                        group.attrs.bars[0].setHeight(group.attrs.lines[0].getY() - activeAnchor.attrs.y);
                    } else if (activeAnchor.attrs.y > lowerLeft.attrs.y) {
                        activeAnchor.attrs.y = lowerLeft.attrs.y;
                    }
                    if (activeAnchor.attrs.x < topLeft.attrs.x) {
                        activeAnchor.attrs.x = topLeft.attrs.x;
                    }
                    topLeft.attrs.y = activeAnchor.attrs.y;
                    lowerRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "lr":
                    if (nStaves > 1) {
                        if (activeAnchor.attrs.y < group.attrs.lines[group.attrs.lines.length - 1].getY()) {
                            activeAnchor.attrs.y = group.attrs.lines[group.attrs.lines.length - 1].getY();
                        }
                        group.attrs.bars[group.attrs.bars.length - 1].setHeight(activeAnchor.attrs.y - group.attrs.lines[group.attrs.lines.length - 1].getY());
                    } else if (activeAnchor.attrs.y < topLeft.attrs.y) {
                        activeAnchor.attrs.y = topLeft.attrs.y;
                    }
                    if (activeAnchor.attrs.x < topLeft.attrs.x) {
                        activeAnchor.attrs.x = topLeft.attrs.x;
                    }
                    lowerLeft.attrs.y = activeAnchor.attrs.y;
                    topRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "ll":
                    if (nStaves > 1) {
                        if (activeAnchor.attrs.y < group.attrs.lines[group.attrs.lines.length - 1].getY()) {
                            activeAnchor.attrs.y = group.attrs.lines[group.attrs.lines.length - 1].getY();
                        }
                        group.attrs.bars[group.attrs.bars.length - 1].setHeight(activeAnchor.attrs.y - group.attrs.lines[group.attrs.lines.length - 1].getY());
                    } else if (activeAnchor.attrs.y < topLeft.attrs.y) {
                        activeAnchor.attrs.y = topLeft.attrs.y;
                    }
                    if (activeAnchor.attrs.x > topRight.attrs.x) {
                        activeAnchor.attrs.x = topRight.attrs.x;
                    }
                    lowerRight.attrs.y = activeAnchor.attrs.y;
                    topLeft.attrs.x = activeAnchor.attrs.x;
                    break;
            }

            var width = topRight.attrs.x - topLeft.attrs.x;
            var height = lowerLeft.attrs.y - topLeft.attrs.y;

            bar.setPosition(topLeft.attrs.x, topLeft.attrs.y);
            iBox.setPosition(topLeft.attrs.x - 5, topLeft.attrs.y - 5);
            bar.setSize(width, height);
            iBox.setSize(width + 10, height + 10);

            if (nStaves > 1) {
                var i;
                for (i = 0; i < group.attrs.lines.length; i++) {
                    group.attrs.lines[i].setX(topLeft.attrs.x);
                    group.attrs.lines[i].setWidth(width);
                }
                for (i = 0; i < group.attrs.bars.length; i++) {
                    group.attrs.bars[i].setX(topLeft.attrs.x);
                    group.attrs.bars[i].setWidth(width);
                }

            }
        };

        var refitBox = function(bGroup) {
            // The various components of a bar
            var topLeft = bGroup.get(".tl")[0];
            var topRight = bGroup.get(".tr")[0];
            var lowerRight = bGroup.get(".lr")[0];
            var lowerLeft = bGroup.get(".ll")[0];
            var bar = bGroup.get(".bar")[0];
            var iBox = bGroup.get(".barbox")[0];
            var barNumber = bGroup.get(".barnumber")[0];
            var lines = bGroup.attrs.lines;
            var bars = bGroup.attrs.bars;

            var tlPos = topLeft.getAbsolutePosition();
            var lrPos = lowerRight.getAbsolutePosition();

            var width = lrPos.x - tlPos.x;
            var height = lrPos.y - tlPos.y;

            // Reassign element positions

            var i, absY;
            for (i = 0; i < lines.length; i++) {
                absY = lines[i].getAbsolutePosition().y - tlPos.y;
                lines[i].setPosition({
                    x: 0,
                    y: absY
                });
            }
            for (i = 0; i < bars.length; i++) {
                absY = bars[i].getAbsolutePosition().y - tlPos.y;
                bars[i].setPosition({
                    x: 0,
                    y: absY
                });
            }

            bGroup.setPosition({
                x: tlPos.x,
                y: tlPos.y
            });
            barNumber.setPosition({
                x: 0,
                y: 0
            });
            bar.setPosition({
                x: 0,
                y: 0
            });
            iBox.setPosition({
                x: -barMargin,
                y: -barMargin
            });
            topLeft.setPosition({
                x: 0,
                y: 0
            });
            topRight.setPosition({
                x: width,
                y: 0
            });
            lowerRight.setPosition({
                x: width,
                y: height
            });
            lowerLeft.setPosition({
                x: 0,
                y: height
            });

            // Reassign element dimensions
            bar.setWidth(width);
            bar.setHeight(height);
            iBox.setWidth(width + (barMargin * 2));
            iBox.setHeight(height + (barMargin * 2));

            barNumber.setFontSize(textSize);
            if (width < (barNumber.getTextWidth() + 6)) {
                barNumber.setFontSize(textSize * (width / (barNumber.getTextWidth() + 6)));
            }
            if (height < (barNumber.getTextHeight() + 6)) {
                barNumber.setFontSize(textSize * (height / (barNumber.getTextHeight() + 6)));
            }
        };

        /* Resize/relocate a system to correctly bound its bars.
         * Used for maintaining system dimensions for bar-system membership detection
         * and MEI generation */
        var resizeSystem = function(system) {
            var bars = system.getLayer().get(".bar");
            var tlx = -1;
            var tly = -1;
            var lrx = -1;
            var lry = -1;
            var i;
            for (i = 0; i < bars.length; i++) {
                var barPos = bars[i].getAbsolutePosition();

                var rightX = barPos.x + bars[i].getWidth();
                var lowerY = barPos.y + bars[i].getHeight();
                if (tlx === -1 || barPos.x < tlx) {
                    tlx = barPos.x;
                }
                if (tly === -1 || barPos.y < tly) {
                    tly = barPos.y;
                }
                if (lrx === -1 || rightX > lrx) {
                    lrx = rightX;
                }
                if (lry === -1 || lowerY > lry) {
                    lry = lowerY;
                }
            }

            system.attrs.x = tlx;
            system.attrs.y = tly;
            system.attrs.width = lrx - tlx;
            system.attrs.height = lry - tly;
            /*
            // TEST CODE FOR VISIBLE SYSTEMS
            var tBox = system.get(".testbox")[0];
            tBox.setAbsolutePosition({
                x: tlx,
                y: tly
            });
            tBox.setWidth(lrx - tlx);
            tBox.setHeight(lry - tly);*/
            system.getLayer().draw();
        };

        // Update the numbering of the bars on the page to be in the correct order
        var updateNumbers = function() {
            // Sort ranking function for sorting bars by x-coordinate
            var sortBarsByX = function(a, b) {
                return a.getX() - b.getX();
            };
            var currentNumber = settings.minbar;
            var i, j, changed;
            for (i = 0; i < systems.length; i++) {
                // Sort bars by x-coordinate
                systems[i].attrs.bars = systems[i].attrs.bars.sort(sortBarsByX);
                changed = false;
                for (j = 0; j < systems[i].attrs.bars.length; j++) {
                    // Reassign bar number if the current one is incorrect
                    if (systems[i].attrs.bars[j].attrs.number !== currentNumber) {
                        changed = true;
                        systems[i].attrs.bars[j].attrs.number = currentNumber;
                        var barNumber = systems[i].attrs.bars[j].get(".barnumber")[0];
                        barNumber.setText(currentNumber.toString());
                    }
                    currentNumber++;
                }
                // Only redraw system if changes have occurred
                if (changed) {
                    systems[i].getLayer().draw();
                }
            }
        };

        // Finds the nearest system to a given bar
        var findNearestSystem = function(barGroup) {
            var bar = barGroup.get(".bar")[0];
            var top = bar.getAbsolutePosition().y;
            var lower = top + bar.getHeight();

            var i;
            // Check the corners to see if any are contained in the bar
            for (i = 0; i < systems.length; i++) {
                var containsTop = (top > systems[i].getY()) && (top < systems[i].getY() + systems[i].attrs.height);
                var containsBottom = (lower > systems[i].getY()) && (lower < systems[i].getY() + systems[i].attrs.height);
                if (containsTop || containsBottom) {
                    return systems[i];
                }
            }
            // Find shortest corner distance to a system
            var distances = [];
            for (i = 0; i < systems.length; i++) {
                distances[4 * i] = Math.abs(top - systems[i].getY());
                distances[(4 * i) + 1] = Math.abs(top - (systems[i].getY() + systems[i].attrs.height));
                distances[(4 * i) + 2] = Math.abs(lower - systems[i].getY());
                distances[(4 * i) + 3] = Math.abs(lower - (systems[i].getY() + systems[i].attrs.height));
            }

            var minDist = Math.min.apply(Math, distances);

            for (i = 0; i < distances.length; i++) {
                if (distances[i] === minDist) {
                    return systems[Math.floor(i / 4)];
                }
            }
            return null;
        };

        var addAnchor = function(group, iBox, x, y, name) {
            var stage = group.getStage();
            var layer = group.getLayer();
            var anchor = new Kinetic.Circle({
                x: x,
                y: y,
                stroke: "#666",
                fill: "#ddd",
                strokeWidth: 2,
                radius: 3,
                name: name,
                draggable: true,
                visible: false
            });

            // Update bar when moved
            anchor.on("dragmove", function() {
                update(group, this);
                layer.draw();
            });
            // Prevent event from bubbling up when anchor selected, move bar to top, hide bar number
            anchor.on("mousedown", function(e) {
                group.setDraggable(false);
                this.moveToTop();
                e.cancelBubble = true;
                var number = group.get(".barnumber")[0];
                number.attrs.visible = false;
            });
            // Update score information on dragend (bar/system fitting, bar numbers)
            anchor.on("dragend", function() {
                resizeSystem(group.getParent().get(".system")[0]);
                group.setDraggable(true);
                updateNumbers();
                refitBox(group);
                var number = group.get(".barnumber")[0];
                number.attrs.visible = true;
                layer.draw();
            });
            // Add hover styling
            anchor.on("mouseover", function() {
                var layer = this.getLayer();
                document.body.style.cursor = "pointer";
                this.setStrokeWidth(4);
                layer.draw();
            });
            // Restore hover styling on mouseout
            anchor.on("mouseout", function() {
                var layer = this.getLayer();
                document.body.style.cursor = "move";
                this.setStrokeWidth(2);
                layer.draw();
            });
            // Keep anchor visible during drag
            group.on("mouseover dragmove", function() {
                anchor.attrs.visible = true;
                anchor.getLayer().draw();
            });
            // Hide anchors when mouse leaves bar
            group.on("mouseout", function() {
                anchor.attrs.visible = false;
                anchor.getLayer().draw();
            });
            group.add(anchor);
        };

        var getStaffLines = function(group) {
            var yLines = [];
            var i;
            for (i = 0; i < group.attrs.lines.length; i++) {
                yLines[i] = Math.round(group.attrs.lines[i].getY() + (group.attrs.lines[i].getHeight() / 2));
            }
            return yLines;
        };

        var addStaffLine = function(stage, group, y, w, gH, bar, lineNum, barNum, bottom, numLines) {
            var nStaves = (numLines / 2) + 1;
            var line = new Kinetic.Rect({
                x: 0,
                y: y - 1,
                width: w,
                height: 3,
                fill: 'red',
                name: "line"
            });
            line.on("mouseover", function(evt) {
                document.body.style.cursor = "pointer";
                evt.cancelBubble = true;
            });
            line.on("mouseout", function(evt) {
                document.body.style.cursor = "move";
                evt.cancelBubble = true;
            });
            line.on("mousedown", function(evt) {
                stage.on("mousemove", function(e) {
                    var pos = stage.getMousePosition(e);
                    var pY = pos.y;
                    var gY = group.getY();
                    if (bottom === true) {
                        // Bottom of staff line
                        if (barNum === 0 && pY < gY) {
                            //First line hits top of system
                            pY = gY;
                        } else if (barNum > 0 && pY < (group.attrs.lines[lineNum - 1].getY() + gY)) {
                            //Non-first line hits top of its own staff
                            pY = group.attrs.lines[lineNum - 1].getY() + group.getY();
                        } else if (lineNum < (numLines - 1) && pY > (group.attrs.lines[lineNum + 1].getY() + gY)) {
                            //Line hits top of next staff
                            pY = group.attrs.lines[lineNum + 1].getY() + gY;
                        }
                        bar.setHeight(pY - (bar.getY() + gY));
                    } else {
                        // Top of staff line
                        if (barNum === (nStaves - 1) && pY > (gH + gY)) {
                            //Last line hits bottom of system
                            pY = gH + gY;
                        } else if (barNum < (nStaves - 1) && pY > (group.attrs.lines[lineNum + 1].getY() + gY)) {
                            //Non-last line hits bottom of its own staff
                            pY = group.attrs.lines[lineNum + 1].getY() + gY;
                        } else if (lineNum > 0 && pY < (group.attrs.lines[lineNum - 1].getY() + gY)) {
                            //Line hits bottom of previous staff
                            pY = group.attrs.lines[lineNum - 1].getY() + gY;
                        }
                        var prevBottom = bar.getY() + bar.getHeight();
                        bar.setHeight(prevBottom + gY - pY);
                        bar.setY(pY - gY);
                    }

                    line.setY(pY - gY);
                    group.getLayer().draw();
                });
                stage.on("mouseup", function() {
                    stage.off("mousemove");
                    stage.off("mouseup");
                });
                evt.cancelBubble = true;
            });
            group.attrs.lines.push(line);
            group.add(line);
        };

        var addBar = function(stage, system, x, y, w, h, lines, id, facs, idList, facsList, number) {
            if (id === undefined) {
                id = "";
            }
            if (facs === undefined) {
                facs = "";
            }
            if (idList === undefined) {
                idList = [];
            }
            if (facsList === undefined) {
                facsList = [];
            }
            if (number === undefined) {
                number = 0;
            }
            var bGroup = new Kinetic.Group({
                x: x,
                y: y,
                width: w,
                height: h,
                draggable: true,
                name: "bargroup",
                number: number,
                lines: [],
                bars: [],
                id: id,
                facs: facs
            });

            // Insert bar into correct position in system's bars list
            var i = 0;
            for (i = 0; i < system.children.length; i++) {
                if (system.children[i].getX() > x) {
                    system.attrs.bars.splice(i, 0, bGroup);
                    break;
                }
            }
            if (i === system.children.length) {
                system.attrs.bars.push(bGroup);
            }

            system.add(bGroup);

            // Detection box for bar, coloured near-transparent orange (for now)
            var invisiBox = new Kinetic.Rect({
                x: -settings.barmargin,
                y: -settings.barmargin,
                width: w + (settings.barmargin * 2),
                height: h + (settings.barmargin * 2),
                fill: 'orange',
                alpha: 0.05,
                name: "barbox"
            });
            bGroup.add(invisiBox);

            var bar = new Kinetic.Rect({
                x: 0,
                y: 0,
                width: w,
                height: h,
                fill: '',
                stroke: 'red',
                strokeWidth: 2,
                name: "bar"
            });

            // Pointer styling
            bGroup.on("mouseover", function() {
                this.moveToTop();
                document.body.style.cursor = "move";
            });
            bGroup.on("mouseout", function() {
                document.body.style.cursor = "default";
            });
            // Delete bar if alt-clicked, then re-number and update systems
            bGroup.on("click", function(e) {
                if (e.altKey) {
                    system.getLayer().remove(bGroup);
                    system.attrs.bars.splice(system.attrs.bars.indexOf(bGroup), 1);
                    updateNumbers();
                    resizeSystem(system);
                }
            });
            // Recalculate system membership, and system size on dragend
            bGroup.on("dragend", function(e) {
                var nearSystem = findNearestSystem(this);
                // If the nearest system is not the bar's current system, reassign membership
                if (nearSystem !== system) {
                    system.getLayer().remove(bGroup);
                    system.attrs.bars.splice(system.attrs.bars.indexOf(bGroup), 1);
                    addBar(stage, nearSystem, bGroup.getX(), bGroup.getY(), bar.getWidth(), bar.getHeight(), getStaffLines(bGroup), 0);
                    resizeSystem(nearSystem);
                }
                updateNumbers();
                resizeSystem(system);
                system.getLayer().draw();
                system = nearSystem;
            });

            var nStaves = 1;
            if (lines.length > 1) {
                nStaves = (lines.length / 2) + 1;
            }
            if (nStaves > 1) {
                for (i = 0; i < nStaves; i++) {
                    var lIndex = 2 * i;
                    var lTop = 0;
                    var lBottom = h;
                    if (lIndex > 0) {
                        lTop = lines[lIndex - 1];
                    }
                    if (lIndex < lines.length) {
                        lBottom = lines[lIndex];
                    }
                    var subBar = new Kinetic.Rect({
                        y: lTop,
                        width: w,
                        height: lBottom - lTop,
                        fill: 'blue',
                        alpha: 0.15,
                        stroke: 'black',
                        strokeWidth: 1,
                        name: "subbar",
                        id: idList[i],
                        facs: facsList[i]
                    });
                    bGroup.attrs.bars.push(subBar);
                    bGroup.add(subBar);
                }
            }

            // Split bar if shift-clicked, splitting at location of click
            bar.on("click", function(e) {
                if (e.shiftKey) {
                    var pos = stage.getMousePosition(e);
                    var absBarPos = bar.getAbsolutePosition();
                    var leftWidth = pos.x - absBarPos.x;
                    var rightWidth = absBarPos.x + bar.getWidth() - pos.x;
                    system.getLayer().remove(bGroup);
                    system.attrs.bars.splice(system.attrs.bars.indexOf(bGroup), 1);

                    addBar(stage, system, absBarPos.x, absBarPos.y, leftWidth, bar.getHeight(), getStaffLines(bGroup), 0);
                    addBar(stage, system, pos.x, absBarPos.y, rightWidth, bar.getHeight(), getStaffLines(bGroup), 0);

                    updateNumbers();
                }
            });

            bGroup.add(bar);

            if (nStaves > 1) {
                for (i = 0; i < lines.length; i++) {
                    var barNum = Math.ceil(i / 2);
                    var lineBar = bGroup.attrs.bars[barNum];
                    var bottomLine = false;
                    if ((i % 2) === 0) {
                        bottomLine = true;
                    }
                    addStaffLine(stage, bGroup, lines[i], w, h, lineBar, i, barNum, bottomLine, lines.length);
                }
            }

            // Number text in top-left corner of bar
            var barText = new Kinetic.Text({
                x: 0,
                y: 0,
                fontSize: settings.textsize,
                fontFamily: "Calibri",
                textFill: "white",
                fill: 'black',
                text: number.toString(),
                align: 'center',
                padding: settings.textpadding,
                name: "barnumber"
            });

            if (w < (barText.getTextWidth() + (settings.textpadding * 2))) {
                barText.setFontSize(settings.textsize * (w / (barText.getTextWidth() + 6)));
            }
            if (h < (barText.getTextHeight() + (settings.textpadding * 2))) {
                barText.setFontSize(settings.textsize * (h / (barText.getTextHeight() + 6)));
            }

            bGroup.add(barText);
            // Add anchors to bar
            addAnchor(bGroup, invisiBox, 0, 0, "tl");
            addAnchor(bGroup, invisiBox, w, 0, "tr");
            addAnchor(bGroup, invisiBox, w, h, "lr");
            addAnchor(bGroup, invisiBox, 0, h, "ll");
            // By adding group to layer, bars will not move when system is resized/relocated
            system.getLayer().add(bGroup);
        };

        // Returns the system with the given UUID tag
        var getSystemById = function(id) {
            var i;
            for (i = 0; i < systems.length; i++) {
                if (systems[i].attrs.id === id) {
                    return systems[i];
                }
            }
            return null;
        };

        // Find the nearest system to a given y-coordinate.
        var findNearestSystemToPoint = function(y) {
            var distances = [];
            var i;
            for (i = 0; i < systems.length; i++) {
                distances[2 * i] = Math.abs(y - systems[i].getY());
                distances[(2 * i) + 1] = Math.abs(y - (systems[i].getY() + systems[i].attrs.height));
            }

            var minDist = Math.min.apply(Math, distances);

            for (i = 0; i < distances.length; i++) {
                if (distances[i] === minDist) {
                    return systems[Math.floor(i / 2)];
                }
            }
            return null;
        };
        
        init();
    };
    $.fn.barlinecorrection = function(options)
    {
        return this.each(function()
        {
            var element = $(this);

            // Return early if this element already has a plugin instance
            if (element.data('barlinecorrection'))
            {
                return;
            }

            // pass options to plugin constructor
            var barlineCorrection = new BarlineCorrection(this, options);

            // Store plugin object in this element's data
            element.data('barlinecorrection', barlineCorrection);
        });
    };
})(jQuery);
