(function ($) {
    "use strict";
    $(document).ready(function () {
        //Object used to store background image
        var imageObj = new Image();
    
        //Corner drag update function for a multistaff
        function updateMultiStaffGroup(group, activeAnchor) {
            // The exterior anchors of a multistaff
            var topLeft = group.get(".1")[0];
            var topRight = group.get(".2")[0];
            var bottomRight = group.get(".3")[0];
            var bottomLeft = group.get(".4")[0];
            
            //The outer staff frame of the multistaff
            var staff = group.get(".multistaffframe")[0];
            //The invisible selection box of the multistaff
            var iBox = group.get(".multistaffbox")[0];
            //Prevent anchors from hiding themselves
            topLeft.attrs.visible = true;
            topRight.attrs.visible = true;
            bottomRight.attrs.visible = true;
            bottomLeft.attrs.visible = true;
            
            //Adjust anchor locations depending on which was moved
            switch (activeAnchor.getName()) {
                case "1":
                    topRight.attrs.y = activeAnchor.attrs.y;
                    bottomLeft.attrs.x = activeAnchor.attrs.x;
                    break;
                case "2":
                    topLeft.attrs.y = activeAnchor.attrs.y;
                    bottomRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "3":
                    bottomLeft.attrs.y = activeAnchor.attrs.y;
                    topRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "4":
                    bottomRight.attrs.y = activeAnchor.attrs.y;
                    topLeft.attrs.x = activeAnchor.attrs.x;
                    break;
            }
            
            //Scale multistaff
            var width = topRight.attrs.x - topLeft.attrs.x;
            var height = bottomLeft.attrs.y - topLeft.attrs.y;
            
            //Operations on substaves of multistaff
            var substaves = group.get(".substaff");
            var i;
            for (i = 0; i < substaves.length; i++) {
                var substaff = substaves[i];
                var sIBox = substaff.get(".staffbox")[0];
                var first = substaff.get(".firststaff");
                var last = substaff.get(".laststaff");
                var currStaff = null;
                //First staff's top locks to the top of the multistaff
                if (first.length === 1) {
                    currStaff = first[0];
                    substaff.setPosition(topLeft.attrs.x + 5, topLeft.attrs.y + 5);
                //Last staff's bottom locks to the bottom of the multistaff
                } else if (last.length === 1) {
                    currStaff = last[0];
                    substaff.setPosition(bottomLeft.attrs.x + 5, bottomLeft.attrs.y - 5 - currStaff.getHeight());
                } else {
                    currStaff = substaff.get(".staff")[0];
                    substaff.setX(topLeft.attrs.x + 5);
                }
                if(width && height) {
                    currStaff.setWidth(width - 10);
                    sIBox.setWidth(width);
                }
                
                var number = currStaff.attrs.number;
                //Only right anchors need to be updated, as left side of the substaff is appropriately transposed
                var tr = substaff.get("." + (number * 4 + 2))[0];
                var br = substaff.get("." + (number * 4 + 3))[0];
                
                tr.attrs.x = currStaff.getWidth();
                br.attrs.x = currStaff.getWidth();
            }
            
            // Correct line dimensions
            var lines = group.get(".line");
            for (i = 0; i < lines.length; i++) {
                lines[i].setY(topLeft.attrs.y);
                lines[i].setHeight(height);
                if (lines[i].getX() > width) {
                    topRight.attrs.x = lines[i].getX();
                    bottomRight.attrs.x = topRight.attrs.x;
                    width = lines[i].getX();
                } else if (lines[i].getX() < topLeft.attrs.x) {
                    topLeft.attrs.x = lines[i].getX();
                    bottomLeft.attrs.x = topLeft.attrs.x;
                    width = topRight.attrs.x - topLeft.attrs.x;
                }
            }
            //Adjust position and dimensions of multistaff
            staff.setPosition(topLeft.attrs.x + 5, topLeft.attrs.y + 5);
            iBox.setPosition(topLeft.attrs.x - 5, topLeft.attrs.y - 5);
            if(width && height) {
                staff.setSize(width - 10, height - 10);
                iBox.setSize(width + 10, height + 10);
            }
        }
        
        //Corner drag update function for a substaff
        function updateSubStaff(group, activeAnchor) {
            //Multistaff group for the substaff
            var superGroup = group.getParent();
            var first = group.get(".firststaff");
            var last = group.get(".laststaff");
            var isFirst = false;
            var isLast = false;
        
            var staff = null;
            //TODO
            if (first.length === 1) {
                isFirst = true;
                staff = first[0];
            } else if (last.length === 1) {
                isLast = true;
                staff = last[0];
            } else {
                staff = group.get(".staff")[0];
            }
        
            var number = staff.attrs.number;
        
            var topLeft = group.get("." + (number * 4 + 1))[0];
            var topRight = group.get("." + (number * 4 + 2))[0];
            var bottomRight = group.get("." + (number * 4 + 3))[0];
            var bottomLeft = group.get("." + (number * 4 + 4))[0];
        
            var iBox = group.get(".staffbox")[0];
            topLeft.attrs.visible = true;
            topRight.attrs.visible = true;
            bottomRight.attrs.visible = true;
            bottomLeft.attrs.visible = true;
        
            switch (activeAnchor.getName()) {
                case number * 4 + 1:
                    topRight.attrs.y = activeAnchor.attrs.y;
                    bottomLeft.attrs.x = activeAnchor.attrs.x;
                    break;
                case number * 4 + 2:
                    topLeft.attrs.y = activeAnchor.attrs.y;
                    bottomRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case number * 4 + 3:
                    bottomLeft.attrs.y = activeAnchor.attrs.y;
                    topRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case number * 4 + 4:
                    bottomRight.attrs.y = activeAnchor.attrs.y;
                    topLeft.attrs.x = activeAnchor.attrs.x;
                    break;
            }
            
            var width = topRight.attrs.x - topLeft.attrs.x;
            var height = bottomLeft.attrs.y - topLeft.attrs.y;
            
            //group.setPosition(topLeft.attrs.x, topLeft.attrs.y);
            staff.setPosition(topLeft.attrs.x, topLeft.attrs.y);
            iBox.setPosition(topLeft.attrs.x - 5, topLeft.attrs.y - 5);
            if(width && height) {
                staff.setSize(width, height);
                iBox.setSize(width + 10, height + 10);
            }
        }
        
        //Corner drag update function for a single staff object
        function updateStaff(group, activeAnchor) {
            var topLeft = group.get(".1")[0];
            var topRight = group.get(".2")[0];
            var bottomRight = group.get(".3")[0];
            var bottomLeft = group.get(".4")[0];
            var staff = group.get(".staff")[0];
            var iBox = group.get(".staffbox")[0];
            topLeft.attrs.visible = true;
            topRight.attrs.visible = true;
            bottomRight.attrs.visible = true;
            bottomLeft.attrs.visible = true;
            // Update anchor positions
            switch (activeAnchor.getName()) {
                case "1":
                    topRight.attrs.y = activeAnchor.attrs.y;
                    bottomLeft.attrs.x = activeAnchor.attrs.x;
                    break;
                case "2":
                    topLeft.attrs.y = activeAnchor.attrs.y;
                    bottomRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "3":
                    bottomLeft.attrs.y = activeAnchor.attrs.y;
                    topRight.attrs.x = activeAnchor.attrs.x;
                    break;
                case "4":
                    bottomRight.attrs.y = activeAnchor.attrs.y;
                    topLeft.attrs.x = activeAnchor.attrs.x;
                    break;
            }
    
            var width = topRight.attrs.x - topLeft.attrs.x;
            var height = bottomLeft.attrs.y - topLeft.attrs.y;
    
            var lines = group.get(".line");
            var i;
            for (i = 0; i < lines.length; i++) {
                lines[i].setY(topLeft.attrs.y);
                lines[i].setHeight(height);
                if (lines[i].getX() > width) {
                    topRight.attrs.x = lines[i].getX();
                    bottomRight.attrs.x = topRight.attrs.x;
                    width = lines[i].getX();
                } else if (lines[i].getX() < topLeft.attrs.x) {
                    topLeft.attrs.x = lines[i].getX();
                    bottomLeft.attrs.x = topLeft.attrs.x;
                    width = topRight.attrs.x - topLeft.attrs.x;
                }
            }
            staff.setPosition(topLeft.attrs.x, topLeft.attrs.y);
            iBox.setPosition(topLeft.attrs.x - 5, topLeft.attrs.y - 5);
            if(width && height) {
                staff.setSize(width, height);
                iBox.setSize(width + 10, height + 10);
            }
        }
        
        //Choose update function based on group type
        function update(group, activeAnchor) {
            if (group.getName() === "multistaffgroup") {
                updateMultiStaffGroup(group, activeAnchor);
            } else if (group.getName() === "substaff") {
                updateSubStaff(group, activeAnchor);
            } else {
                updateStaff(group, activeAnchor);
            }
        }
        
        //Add corner anchor to staff
        function addAnchor(group, iBox, x, y, name) {
            var stage = group.getStage();
            var layer = group.getLayer();
            var superGroup = null;
            if (group.getName() === "substaff") {
                superGroup = group.getParent();
            }
            //Invisble by default, becomes visible when iBox is moused over
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
            //Movement behaviours
            anchor.on("dragmove", function() {
                update(group, this);
                layer.draw();
            });
            anchor.on("mousedown touchstart", function(e) {
                group.setDraggable(false);
                this.moveToTop();
                e.cancelBubble = true;
            });
            anchor.on("dragend", function() {
                group.setDraggable(true);
                layer.draw();
            });
            // add hover styling
            anchor.on("mouseover", function() {
                var layer = this.getLayer();
                document.body.style.cursor = "pointer";
                this.setStrokeWidth(4);
                layer.draw();
            });
            anchor.on("mouseout", function() {
                var layer = this.getLayer();
                document.body.style.cursor = "default";
                this.setStrokeWidth(2);
                layer.draw();
            });
            if (superGroup !== null) {
                superGroup.on("dragmove", function(e) {
                    anchor.attrs.visible = true;
                    anchor.getLayer().draw();
                });
                superGroup.on("mouseout", function() {
                    anchor.attrs.visible = false;
                    anchor.getLayer().draw();
                });
            }
            group.on("mouseover dragmove", function() {
                anchor.attrs.visible = true;
                anchor.getLayer().draw();
            });
            group.on("mouseout", function() {
                anchor.attrs.visible = false;
                anchor.getLayer().draw();
            });
            group.add(anchor);
        }
        
        //Adds a line to a staff (only implemented for single staves atm)
        function addLine(stage, group, x, y, height) {
            var line = new Kinetic.Rect({
                x: x - group.getX() - 0.5,
                y: y,
                width: 2,
                height: height,
                fill: 'black',
                name: "line"
            });
            line.on("mousedown", function(evt) {
                stage.on("mousemove", function(e) {
                    var pos = stage.getMousePosition(e);
                    var pX = pos.x;
                    var staff = group.get(".staff")[0];
                    var newPos = pX - group.getX() - 0.5;
                    if (newPos < ( staff.getX() + staff.getWidth()) && newPos > staff.getX()) {
                        line.setX(newPos);
                    } else if (newPos > ( staff.getX() + staff.getWidth())) {
                        newPos = staff.getWidth();
                    } else {
                        newPos = 0;
                    }
                    line.getLayer().draw();
                });
                stage.on("mouseup", function() {
                    stage.off("mousemove");
                    stage.off("mouseup");
                });
                evt.cancelBubble = true;
            });
            line.on("click", function(e) {
                if (e.altKey) {
                    group.remove(line);
                    group.getLayer().draw();
                }
            });
            group.add(line);
        }
        
        //Adds a single staff object
        function addStaff(stage, tl, br, lines) {
            if (lines === undefined) {
                lines = [];
            }
        
            var sWidth = br.x - tl.x;
            var sHeight = br.y - tl.y;
        
            var sGroup = new Kinetic.Group({
                x: tl.x,
                y: tl.y,
                draggable: true,
                name: "staffgroup"
            });
        
            var sLayer = new Kinetic.Layer();
            sLayer.add(sGroup);
        
            var invisiBox = new Kinetic.Rect({
                x: -5,
                y: -5,
                width: sWidth + 10,
                height: sHeight + 10,
                fill: 'red',
                name: "staffbox"
            });
            sGroup.add(invisiBox);

            var staff = new Kinetic.Rect({
                x: 0,
                y: 0,
                width: sWidth,
                height: sHeight,
                fill: '',
                stroke: 'black',
                strokewidth: 4,
                name: "staff"
            });
            sGroup.add(staff);
        
            staff.on("click", function(e) {
                if (e.shiftKey) {
                    var pos = stage.getMousePosition(e);
                    var pX = pos.x;
                    addLine(stage, sGroup, pX, staff.getY(), staff.getHeight());
                    sGroup.getLayer().draw();
                }
            });
        
            var i;
            for (i = 0; i < lines.length; i++) {
                addLine(stage, sGroup, lines[i], 0, sHeight);
            }
        
            addAnchor(sGroup, invisiBox, 0, 0, "1");
            addAnchor(sGroup, invisiBox, sWidth, 0, "2");
            addAnchor(sGroup, invisiBox, sWidth, sHeight, "3");
            addAnchor(sGroup, invisiBox, 0, sHeight, "4");
        
            stage.add(sLayer);
        }
    
        function addStaffBox (group, tl, br, number, total) {
            var sGroup = new Kinetic.Group({
                x: tl.x,
                y: tl.y,
                name: "substaff"
            });
        
            group.add(sGroup);
        
            var sWidth = br.x - tl.x;
            var sHeight = br.y - tl.y;
        
            var sInvisiBox = new Kinetic.Rect({
                x: -5,
                y: -5,
                width: sWidth + 10,
                height: sHeight + 10,
                fill: 'yellow',
                name: "staffbox"
            });
            sGroup.add(sInvisiBox);

            var staff = new Kinetic.Rect({
                x: 0,
                y: 0,
                width: sWidth,
                height: sHeight,
                fill: '',
                stroke: 'black',
                strokewidth: 4,
                name: "staff",
                number: number
            });
        
            if (number === 1) {
                staff.setName("firststaff");
            } else if (number === total) {
                staff.setName("laststaff");
            }
        
            sGroup.add(staff);
            addAnchor(sGroup, sInvisiBox, 0, 0, number * 4 + 1);
            addAnchor(sGroup, sInvisiBox, sWidth, 0, number * 4 + 2);
            addAnchor(sGroup, sInvisiBox, sWidth, sHeight, number * 4 + 3);
            addAnchor(sGroup, sInvisiBox, 0, sHeight, number * 4 + 4);
        }
    
        function addMultiStaff (stage, tl, br, staffEdges, lines) {
            if (staffEdges.length % 2 !== 0 || staffEdges.length === 0) {
                return "Badly formed arguments";
            }
            var nStaves = (staffEdges.length / 2) + 1;
            if (lines === undefined) {
                lines = [];
            }
        
            var msWidth = br.x - tl.x;
            var msHeight = br.y - tl.y;
        
            var msGroup = new Kinetic.Group({
                x: tl.x,
                y: tl.y,
                draggable: true,
                name: "multistaffgroup"
            });
        
            var msLayer = new Kinetic.Layer();
            msLayer.add(msGroup);
        
            var invisiBox = new Kinetic.Rect({
                x: -10,
                y: -10,
                width: msWidth + 20,
                height: msHeight + 20,
                fill: 'green',
                name: "multistaffbox"
            });
            msGroup.add(invisiBox);
        
            var staffFrame = new Kinetic.Rect({
                x: 0,
                y: 0,
                width: msWidth,
                height: msHeight,
                fill: '',
                stroke: 'black',
                strokewidth: 4,
                name: "multistaffframe"
            });
            msGroup.add(staffFrame);
        
        
            var i, staffTL, staffBR;
            for (i = 1; i <= nStaves; i++) {
                if (i === 1) {
                    staffTL = {
                        x: 0,
                        y: 0
                    };
                } else {
                    staffTL = {
                        x: 0,
                        y: staffEdges[(2 * i) - 3]
                    };
                } 
                if (i === nStaves) {
                    staffBR = {
                        x: msWidth,
                        y: msHeight
                    };
                } else {
                    staffBR = {
                        x: msWidth,
                        y: staffEdges[(2 * i) - 2]
                    };
                }
                addStaffBox(msGroup, staffTL, staffBR, i, nStaves);
            }
        
            addAnchor(msGroup, invisiBox, -5, -5, "1");
            addAnchor(msGroup, invisiBox, msWidth+5, -5, "2");
            addAnchor(msGroup, invisiBox, msWidth+5, msHeight+5, "3");
            addAnchor(msGroup, invisiBox, -5, msHeight+5, "4");
        
            stage.add(msLayer);
        }
    
        imageObj.onload = function () {
            var stage = new Kinetic.Stage({
                container: 'imview',
                width: imageObj.width,
                height: imageObj.height
            });
        
            var img = new Kinetic.Image({
                x: 0,
                y: 0,
                image: imageObj
            });
        
            var iLayer = new Kinetic.Layer();
            iLayer.add(img);
            stage.add(iLayer);
        
            var tl = {
                x: 50,
                y: 50
            };
            var br = {
                x: 350,
                y: 220
            };
            var lines = [];
            lines[0] = 70;
            lines[1] = 100;
            var staffEdges = [];
            staffEdges[0] = 50;
            staffEdges[1] = 75;
            staffEdges[2] = 105;
            staffEdges[3] = 130;
            addMultiStaff(stage, tl, br, staffEdges, lines);
        };
    
        imageObj.src = 'static/images/IMG_8478_600.jpg';
    });
})(jQuery);
