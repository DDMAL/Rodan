import $ from 'jquery';
import _ from "underscore";
import Backbone from "backbone";
import Marionette from "marionette";
import Class from "models/Class";
import ClassEvents from "events/ClassEvents";
import GlyphEvents from "events/GlyphEvents";
import PageEvents from "events/PageEvents";
import MainMenuEvents from "events/MainMenuEvents";
import GlyphCollection from "collections/GlyphCollection";
import ClassTreeView from "views/ClassTree/ClassTreeView";
import ClassTreeViewModel from "views/ClassTree/ClassTreeViewModel";
import GlyphEditView from "views/GlyphEdit/GlyphEditView";
import ClassEditView from "views/ClassEdit/ClassEditView";
import GlyphMultiEditView from "views/GlyphMultiEdit/GlyphMultiEditView";
import TrainingEditView from "views/TrainingEdit/TrainingEditView";
import GlyphTableView from "views/GlyphTable/GlyphTableView";
import GlyphTableRowViewModel from "views/GlyphTable/Row/GlyphTableRowViewModel";
import GlyphTableRowCollection from "views/GlyphTable/Row/GlyphTableRowCollection";
import ImagePreviewView from "views/ImagePreview/ImagePreviewView";
import ImagePreviewViewModel from "views/ImagePreview/ImagePreviewViewModel";
import RadioChannels from "radio/RadioChannels";
import Strings from "localization/Strings";
import Timer from "utils/Timer";
import template from "./rodan-dashboard.template.html";
// import each from "underscore";

var RodanDashboardView = Marionette.LayoutView.extend(
    /**
     * @lends RodanDashboardView.prototype
     */
    {
        template,
        regions: {
            classCreateRegion: ".glyph-class-create-region",
            glyphTreeRegion: ".glyph-class-tree-region",
            glyphTableRegion: ".glyph-table-region",
            classifierTableRegion: ".classifier-table-region",
            glyphEditRegion: ".glyph-edit-region",
            pagePreviewRegion: ".page-image-preview-region",
            modalTestRegion: ".modal-test"
        },

        events: {
            "mousedown": "onMouseDown",
            "click #save": "saveChanges",
            "click #revert": "revertChanges",
            "click #zoom-out": "zoomOut",
            "click #zoom-in": "zoomIn"
        },

        classifierCount: 0,
        pageCount: 0,
        selectedCount: 0,
        zoomCount: 0,
        zoomLevel: 1.15,
        maxZoomCount: 10,
        isZoomIn: undefined,

        /**
         * @class RodanDashboardView
         *
         * This view is the main "dashboard" of the application.  This view handles
         * most of the glyph editing functionality and determines which editing
         * views the user can see.
         *
         * @constructs
         */
        initialize: function () {
            // Create the preview window
            this.previewView = new ImagePreviewView({
                model: new ImagePreviewViewModel({
                    backgroundImage: this.model.get("previewImage")
                })
            });
            this.isMouseDown = true;
            // Construct the glyph table data structure
            this.trainingRowCollection = new GlyphTableRowCollection();
            this.trainingRowCollection.setClassifier(true);
            this.tableRowCollection = new GlyphTableRowCollection();
            this.tableRowCollection.setClassifier(false);

            this.listenTo(RadioChannels.edit, PageEvents.changeBackground,
                function () {
                    // This makes it so the classes switch color
                    // so it's obvious to which class each glyph belongs
                    // TODO: This should be improved so only one loop
                    var els = document.getElementsByClassName("table table-hover")[0].childNodes;
                    // White and grey
                    var colors = ["white", "gainsboro"];
                    for (var i = 0; i < els.length; i++) {
                        // Alternating
                        var index = i % 2;
                        els[i].style.backgroundColor = colors[index];
                    }
                    els = document.getElementsByClassName("table table-hover")[1].childNodes;
                    for (var j = 0; j < els.length; j++) {
                        // Alternating
                        index = j % 2;
                        els[j].style.backgroundColor = colors[index];
                    }
                }
            );

            // Selected Glyphs
            this.selectedGlyphs = new Backbone.Collection();
            var that = this;
            this.listenTo(RadioChannels.edit, GlyphEvents.selectGlyph,
                function (glyph) {
                    that.selectedGlyphs.add(glyph);
                    that.selectedCount = that.selectedGlyphs.length;
                    document.getElementById("count-selected").innerHTML = that.selectedCount;
                }
            );
            this.listenTo(RadioChannels.edit, GlyphEvents.deselectGlyph,
                function (glyph) {
                    that.selectedGlyphs.remove(glyph);
                    that.selectedCount = that.selectedGlyphs.length;
                    document.getElementById("count-selected").innerHTML = that.selectedCount;
                    if (that.selectedCount === 0) {
                        this.clearEditRegion();
                    }
                }
            );
            this.listenTo(RadioChannels.edit, GlyphEvents.deselectAllGlyphs,
                function () {
                    that.selectedGlyphs.reset();
                    that.selectedCount = 0;
                    document.getElementById("count-selected").innerHTML = that.selectedCount;
                    this.clearEditRegion();
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.addGlyph,
                function (glyph, className) {
                    that.tableRowCollection.addGlyph(glyph, className);
                    // jscs:disable
                    if (className.toLowerCase() !== "unclassified" && !className.startsWith("_group._part") && !className.startsWith("_split")) {
                        that.trainingRowCollection.addGlyph(glyph, className);
                    }
                    // jscs:enable
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.deleteGlyphs,
                function (glyphs) {
                    for (var i = 0; i < glyphs.length; i++) {
                        var glyph = glyphs[i];
                        that.tableRowCollection.deleteGlyph(glyph);
                        that.trainingRowCollection.deleteGlyph(glyph);
                        that.selectedGlyphs.remove(glyph);
                        if (glyph.get("is_training"))
                        {
                            that.classifierCount--;
                        }
                        else if (glyph.get("id_state_manual")) {
                            that.classifierCount--;
                            that.pageCount--;
                        }
                        else {
                            that.pageCount--;
                        }
                    }
                    that.selectedCount = 0;
                    document.getElementById("count-classifier").innerHTML = that.classifierCount;
                    document.getElementById("count-page").innerHTML = that.pageCount;
                    document.getElementById("count-selected").innerHTML = that.selectedCount;

                    this.clearEditRegion();

                    that.previewView.unhighlightGlyphs();
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.setGlyphName,
                function (className) {
                    //Don't add the new class if it's already in the list or if it's a part of a group or a split
                    if (!className.startsWith("_group._part") && !className.startsWith("_split")) {
                        var index = that.model.get('classNames').findIndex(name => name === className);
                        if (index === -1) {
                            var classNameList = that.model.get('classNames').push(className);
                            classNameList = that.model.get('classNames').sort();
                            that.model.set('classNames', classNameList);
                        }
                    }
                }
            );
            // Class editing events
            this.listenTo(RadioChannels.edit, ClassEvents.openClassEdit,
                function (className) {
                    that.openClassEdit(className);
                });

            this.listenTo(RadioChannels.edit, ClassEvents.deleteClass,
                function (className) {
                    var classes = this.model.get('classNames');
                    for (var i = 0; i < classes.length; i++) {
                        var name = classes[i];
                        if (name === className || name.startsWith(className + ".")) {
                            that.tableRowCollection.deleteClass(name);
                            that.trainingRowCollection.deleteClass(name);
                        }
                    }
                    var newClasses = this.model.get('classNames').filter(function (name) {
                        return !name.startsWith(className + ".") && name !== className;
                    });
                    this.model.set('classNames', newClasses);
                    this.clearEditRegion();
                    RadioChannels.edit.trigger(PageEvents.changeBackground);
                });

            this.listenTo(RadioChannels.edit, ClassEvents.renameClass,
                function (oldName, newName) {
                    var classes = this.model.get('classNames');
                    for (var i = 0; i < classes.length; i++) {
                        var name = classes[i];
                        if (name === oldName || name.startsWith(oldName + ".")) {
                            that.tableRowCollection.renameClass(name, oldName, newName);
                            that.trainingRowCollection.renameClass(name, oldName, newName);
                        }
                    }
                    for (var j = 0; j < classes.length; j++) {
                        if (classes[j] === oldName || classes[j].startsWith(oldName + ".")) {
                            classes[j] = classes[j].replace(oldName, newName);
                        }
                    }
                    //remove duplicates
                    var renamedClasses = classes.filter(function (item, pos) {
                        return classes.indexOf(item) === pos;
                    });
                    this.model.set('classNames', renamedClasses);
                    this.openClassEdit(newName);
                    RadioChannels.edit.trigger(PageEvents.changeBackground);
                });

            // Glyph Editing Events
            this.listenTo(RadioChannels.edit, GlyphEvents.openGlyphEdit,
                function (model) {
                    // If it's a training glyph, open the training edit view
                    if (model.attributes.is_training) {
                        that.selectedGlyphs.add(model);
                        that.openTrainingEdit(that.selectedGlyphs);
                    }
                    else {
                        that.previewView.highlightGlyph([model]);
                        that.openGlyphEdit(model);
                    }
                });
            this.listenTo(RadioChannels.edit, GlyphEvents.moveGlyph,
                function (glyph, oldClassName, newClassName) {
                    if (glyph.attributes.is_training) {
                        that.trainingRowCollection.moveGlyph(glyph, oldClassName, newClassName);
                    }
                    else {
                        that.tableRowCollection.moveGlyph(glyph, oldClassName, newClassName);
                        that.trainingRowCollection.moveGlyph(glyph, oldClassName, newClassName);
                    }
                    that.pageCount = 0;
                    that.classifierCount = 0;
                    that.tableRowCollection.each(function (row) {
                        var glyphs = row.get("glyphs");
                        that.pageCount += glyphs.length;
                    });
                    that.trainingRowCollection.each(function (row) {
                        var glyphs = row.get("glyphs");
                        that.classifierCount += glyphs.length;
                    });
                    document.getElementById("count-classifier").innerHTML = that.classifierCount;
                    document.getElementById("count-page").innerHTML = that.pageCount;
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.groupGlyphs,
                function () {
                    that.classifierCount++;
                    that.pageCount++;
                    document.getElementById("count-selected").innerHTML = 1;
                    document.getElementById("count-classifier").innerHTML = that.classifierCount;
                    document.getElementById("count-page").innerHTML = that.pageCount;
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.splitGlyph,
                function () {
                    // After splitting, wait for the DOM to update, then update the count variables
                    var waitTime = 1000;
                    setTimeout(function () {
                        var newPageCount = parseInt($("#count-page").text());
                        var newClassifierCount = parseInt($("#count-classifier").text());
                        that.pageCount = newPageCount;
                        that.classifierCount = newClassifierCount;
                    }, waitTime);
                }
            );
            this.listenTo(RadioChannels.edit, PageEvents.zoom,
                function (zoomLevel, isZoomIn) {
                    var pic = document.getElementsByClassName("preview-background")[0];
                    var oldHeight = pic.height;
                    var newHeight;
                    if (isZoomIn) {
                        newHeight = oldHeight * zoomLevel;
                    }
                    else {
                        newHeight = oldHeight / zoomLevel;
                    }
                    pic.style.height = newHeight + "px";
                    // makes sure the boxes around the glyphs follow the zoom
                    RadioChannels.edit.trigger(GlyphEvents.highlightGlyphs, that.selectedGlyphs);
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.highlightGlyphs,
                function (highlightedGlyphs) {
                    var glyphs = [];
                    for (var i = 0; i < highlightedGlyphs.length; i++) {
                        var glyph = highlightedGlyphs.at(i);
                        glyphs.push(glyph);
                    }
                    that.previewView.highlightGlyph(glyphs);
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.openMultiEdit,
                function () {
                    // If there are no glyphs selected, then close the multi edit view
                    if (that.selectedGlyphs.length === 0) {
                        that.clearEditRegion();
                        return;
                    }
                    // If some of the glyphs selected are training glyphs
                    var training_glyphs = new Backbone.Collection();
                    var glyphs = new Backbone.Collection();
                    // Separating training glyphs from page glyphs
                    for (var i = 0; i < that.selectedGlyphs.length; i++) {
                        var glyph = that.selectedGlyphs.at(i);
                        var name = glyph.attributes.class_name;
                        if (name.startsWith("_group") || name.startsWith("_split")) {
                            // don't add to either window
                        }
                        else if (glyph.attributes.is_training) {
                            training_glyphs.add(glyph);
                        }
                        else {
                            glyphs.add(glyph);
                        }
                    }
                    // Only page glyphs are selected
                    if (training_glyphs.length === 0) {
                        if (glyphs.length === 1) {
                            that.openGlyphEdit(glyphs.at(0));
                        }
                        else {
                            that.openMultiGlyphEdit(glyphs);
                        }
                        RadioChannels.edit.trigger(GlyphEvents.highlightGlyphs, glyphs);
                    }
                    // At least one training glyph is selected
                    else {
                        that.openTrainingEdit(that.selectedGlyphs);
                    }
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.openTrainingEdit,
                function () {
                    that.openTrainingEdit(that.selectedGlyphs);
                }
            );
        },

        onShow: function () {
            var timer = new Timer("RodanDashboardView onShow");

            // Create the preview
            this.pagePreviewRegion.show(this.previewView);

            timer.tick();

            var glyphDictionary = this.model.get("glyphDictionary");
            var classNames = this.model.get("classNames");
            var trainingGlyphs = this.model.get("trainingGlyphs");

            // Show the tree
            this.glyphTreeRegion.show(new ClassTreeView({
                model: new ClassTreeViewModel({
                    class_names: classNames
                })
            }));

            timer.tick();

            var glyphCollections = {};
            var trainingGlyphsCollection = {};

            // Separate the glyphs by their class
            for (var i = 0; i < classNames.length; i++) {
                var glyphs = new GlyphCollection(glyphDictionary[classNames[i]]);
                if (glyphs.length > 0) {
                    glyphCollections[classNames[i]] = glyphs;
                }
                if (trainingGlyphs) {
                    glyphs = new GlyphCollection(trainingGlyphs[classNames[i]]);
                    if (glyphs.length > 0) {
                        trainingGlyphsCollection[classNames[i]] = glyphs;
                    }
                }
            }

            timer.tick("pre-final render");

            var that = this;
            _.each(classNames, function (className) {
                if (glyphCollections[className]) {
                    var row = new GlyphTableRowViewModel({
                        class_name: className,
                        glyphs: glyphCollections[className]
                    });
                    that.pageCount += glyphCollections[className].length;
                    that.tableRowCollection.add(row);
                }
                if (trainingGlyphsCollection[className]) {
                    row = new GlyphTableRowViewModel({
                        class_name: className,
                        glyphs: trainingGlyphsCollection[className]
                    });
                    that.classifierCount += trainingGlyphsCollection[className].length;
                    that.trainingRowCollection.add(row);
                }
            });

            document.getElementById("count-classifier").innerHTML = this.classifierCount;
            document.getElementById("count-page").innerHTML = this.pageCount;
            document.getElementById("count-selected").innerHTML = this.selectedCount;

            timer.tick();

            this.glyphTableRegion.show(new GlyphTableView({
                collection: this.tableRowCollection
            }));
            this.classifierTableRegion.show(new GlyphTableView({
                collection: this.trainingRowCollection
            }));

            RadioChannels.edit.trigger(PageEvents.changeBackground);

            // This section deals with resizing.

            const toggleClassifierGlyphs = () => {
                $("#right0").toggle();
                that.collapsePanes();
            }

            const togglePageGlyphs = () => {
                $("#right1").toggle();
                that.collapsePanes();
            }

            const togglePreviewImage = () => {
                $("#right2").toggle();
                that.collapsePanes();
            }

            $("#collapse-button").on("click", toggleClassifierGlyphs);
            $("#collapse-page").on("click", togglePageGlyphs);
            $("#collapse-image").on("click", togglePreviewImage);

            this.collapseHeight = document.getElementById("collapse-button").getClientRects()[0].height;
            this.collapseWidth = document.getElementById("collapse-button").getClientRects()[0].width;
            this.winWidth = window.innerWidth;
            this.winHeight = window.innerHeight;
            this.navHeight = 125;
            var panesHeight = window.innerHeight - this.navHeight;

            this.classifierRatio = document.getElementById("right0").getClientRects()[0].height / panesHeight;
            this.pageRatio = document.getElementById("right1").getClientRects()[0].height / panesHeight;
            this.imageRatio = document.getElementById("right2").getClientRects()[0].height / panesHeight;
            that.widthRatio = document.getElementById("left1").getClientRects()[0].width / window.innerWidth;

            var elms = document.getElementsByClassName("glyph-image-container");
            for (i = 0; i < elms.length; i++) {
                var child = elms[i].childNodes[0].childNodes[1].childNodes[1];
                child.dataset.originalWidth = child.getAttribute("width");
                child.dataset.originalHeight = child.getAttribute("height");
            }

            var collapsePane = document.getElementById("collapse-pane");
            var countPanel = document.getElementById("upper");
            var classifier = document.getElementById("right0");
            var page = document.getElementById("right1");
            var image = document.getElementById("right2");
            var classEdit = document.getElementById("left1");
            var glyphEdit = document.getElementById("left2");

            page.style.top = classifier.getClientRects()[0].bottom + "px";
            image.style.top = page.getClientRects()[0].bottom + "px";
            image.style.height = window.innerHeight - page.getClientRects()[0].bottom + "px";

            // Hide the classifier glyphs by default. 
            // Note: This should probably be done in a declarative way but would likely require a lot of changes and would be more risky.
            // This method seems to work well for now.
            toggleClassifierGlyphs();

            $(document).mousedown(function ()
            {
                that.isMouseDown = true;
            });
            
            $(document).mousemove(function (event)
            {
                var resizeClass = false;
                if (that.isMouseDown) {
                    if (event.buttons === 0) {
                        that.isMouseDown = false;
                    }

                    // Maintain height of the collapse buttons
                    collapsePane.style.height = that.collapseHeight + "px";

                    var classEditRight = classEdit.getClientRects()[0].left + classEdit.getClientRects()[0].width;
                    var classEditBottom = classEdit.getClientRects()[0].top + classEdit.getClientRects()[0].height;

                    // resizeClass is set to true only if the resize button is clicked and dragged
                    if (event.clientX < classEditRight && event.clientX > (classEditRight - 20) &&
                        event.clientY < classEditBottom && event.clientY > (classEditBottom - 20)) {
                        resizeClass = true;
                    }

                    // Update the widths and heights of the panes
                    // according to where the class names region was dragged
                    if (resizeClass) {
                        classEdit.style.width = event.clientX + "px";
                        glyphEdit.style.width = classEdit.getClientRects()[0].width + "px";
                        classEdit.style.height = event.clientY + "px";

                        var rightWidth = window.innerWidth - classEdit.getClientRects()[0].right + "px";
                        countPanel.style.width = rightWidth;
                        classifier.style.width = rightWidth;
                        page.style.width = rightWidth;
                        image.style.width = rightWidth;

                        var left = classEdit.getClientRects()[0].right;
                        countPanel.style.left = left + "px";
                        image.style.left = left + "px";
                        page.style.left = left + "px";
                        classifier.style.left = left + "px";
                        collapsePane.style.left = left + "px";

                        that.widthRatio = classEdit.getClientRects()[0].width / window.innerWidth;
                    }
                    // Make sure the panels fill the browser window
                    if (image.getClientRects()[0]) {
                        that.imageRatio = image.getClientRects()[0].height / panesHeight;
                    }
                    if (classifier.getClientRects()[0]) {
                        that.classifierRatio = classifier.getClientRects()[0].height / panesHeight;
                        if (page.getClientRects()[0]) {
                            that.pageRatio = page.getClientRects()[0].height / panesHeight;
                            if (image.getClientRects()[0]) {
                                image.style.height = window.innerHeight - page.getClientRects()[0].bottom + "px";
                            }
                            else {
                                page.style.height = window.innerHeight - classifier.getClientRects()[0].bottom + "px";
                            }
                        }
                        else {
                            if (image.getClientRects()[0]) {
                                image.style.height = window.innerHeight - classifier.getClientRects()[0].bottom + "px";
                            }
                        }
                    }
                    else {
                        if (page.getClientRects()[0]) {
                            that.pageRatio = page.getClientRects()[0].height / panesHeight;
                            if (image.getClientRects()[0]) {
                                image.style.height = window.innerHeight - page.getClientRects()[0].bottom + "px";
                            }
                        }
                    }
                    that.rePosition();
                }

            });

            $(window).on("keydown", (event) => {
                // Handle navigation using the arrow keys
                if ((event.key === "ArrowRight" || event.key === "ArrowLeft")) {
                    let nextGlyph = null;
                    // If a glyph is selected, switch to the next glyph
                    if (this.selectedGlyphs.length > 0) {
                        // Find the current glyph index
                        const glyph = this.selectedGlyphs.at(0);
                        const index = glyph.collection.indexOf(glyph);

                        // Find the next glyph to switch to
                        if (event.key === "ArrowRight" && index < glyph.collection.length - 1) {
                            nextGlyph = glyph.collection.at(index + 1);
                        } else if (event.key === "ArrowLeft" && index > 0) {
                            nextGlyph = glyph.collection.at(index - 1);
                        }
                    }
                    // Otherwise if there is at least one glyph in the page, switch to the first glyph
                    else if (this.tableRowCollection.length > 0 && this.tableRowCollection.at(0).attributes.glyphs.length > 0) {
                        nextGlyph = this.tableRowCollection.at(0).attributes.glyphs.at(0);
                    }

                    if (nextGlyph) {
                        // Switch to the prev/next glyph and open glyph edit
                        RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, nextGlyph.attributes.id, true);
                        RadioChannels.edit.trigger(GlyphEvents.deselectAllGlyphs);
                        RadioChannels.edit.trigger(GlyphEvents.selectGlyph, nextGlyph);
                        RadioChannels.edit.trigger(GlyphEvents.openGlyphEdit, nextGlyph);

                        // Scroll the glyph into view
                        document.getElementById(nextGlyph.attributes.id).scrollIntoView();
                    }
                }
            });

            $(window).resize(function () {
                var currentWinHeight = window.innerHeight;
                var currentWinWidth = window.innerWidth;
                var panesHeight = window.innerHeight - that.navHeight;

                document.getElementById("collapse-pane").style.height = that.collapseHeight + "px";

                // If the height of the browser changed, update the heights of the panes
                if (that.winHeight !== currentWinHeight) {
                    if (classifier.getClientRects()[0]) {
                        classifier.style.height = that.classifierRatio * panesHeight + "px";
                        if (page.getClientRects()[0]) {
                            if (image.getClientRects()[0]) {
                                page.style.height = that.pageRatio * panesHeight + "px";
                                image.style.height = currentWinHeight - page.getClientRects()[0].bottom + "px";
                            }
                            else {
                                page.style.height = currentWinHeight - classifier.getClientRects()[0].bottom + "px";
                            }
                        }
                        else {
                            if (image.getClientRects) {
                                image.style.height = currentWinHeight - classifier.getClientRects()[0].bottom + "px";
                            }
                        }
                    }
                    else {
                        if (page.getClientRects()[0]) {
                            page.style.height = that.pageRatio * panesHeight + "px";
                            if (image.getClientRects()[0]) {
                                image.style.height = currentWinHeight - page.getClientRects()[0].bottom + "px";
                            }
                        }
                        else {
                            if (image.getClientRects()[0]) {
                                image.style.height = that.imageRatio * panesHeight + "px";
                            }
                        }
                    }
                    that.winHeight = currentWinHeight;
                }
                that.rePosition();
                // If the width of the browser window changed, update the widths of the panes
                if (that.winWidth !== currentWinWidth) {
                    classEdit.style.width = that.widthRatio * currentWinWidth + "px";
                    glyphEdit.style.width = that.widthRatio * currentWinWidth + "px";

                    var width = window.innerWidth - classEdit.getClientRects()[0].width;
                    countPanel.style.width = width + "px";
                    classifier.style.width = width + "px";
                    page.style.width = width + "px";
                    image.style.width = width + "px";

                    var left = classEdit.getClientRects()[0].right;
                    collapsePane.style.left = left + "px";
                    countPanel.style.left = left + "px";
                    image.style.left = left + "px";
                    page.style.left = left + "px";
                    classifier.style.left = left + "px";

                    that.winWidth = currentWinWidth;
                }
            });
            timer.tick("final");
        },

        collapsePanes: function () {
            this.isMouseDown = false;
            var classifier = document.getElementById("right0");
            var page = document.getElementById("right1");
            var image = document.getElementById("right2");
            var height = window.innerHeight;
            var panesHeight = height - this.navHeight;

            var collClassifier = document.getElementById("collapse-button");
            var collPage = document.getElementById("collapse-page");
            var collImage = document.getElementById("collapse-image");

            if (classifier.getClientRects()[0]) {
                classifier.style.height = panesHeight / 3 + "px";
                if (page.getClientRects()[0]) {
                    page.style.top = classifier.getClientRects()[0].bottom + "px";
                    if (image.getClientRects()[0]) {
                        page.style.height = panesHeight / 3 + "px";
                        image.style.height = height - page.getClientRects()[0].bottom + "px";
                    }
                    else {
                        page.style.height = height - classifier.getClientRects()[0].bottom + "px";
                    }
                }
                else {
                    if (image.getClientRects()[0]) {
                        classifier.style.height = panesHeight / 3 + "px";
                        image.style.height = height - classifier.getClientRects()[0].bottom + "px";
                    }
                    else {
                        classifier.style.height = panesHeight + "px";
                    }
                }
            }
            else {
                if (page.getClientRects()[0]) {
                    page.style.top = collClassifier.getClientRects()[0].bottom + "px";
                    if (image.getClientRects()[0]) {
                        page.style.height = panesHeight / 3 + "px";
                        image.style.height = height - page.getClientRects()[0].bottom + "px";
                    }
                    else {
                        page.style.height = panesHeight + "px";
                    }
                }
                else {
                    if (image.getClientRects()[0]) {
                        image.style.height = panesHeight + "px";
                    }
                }
            }

            if (classifier.getClientRects()[0]) {
                collClassifier.style.background = "white";
                this.classifierRatio = classifier.getClientRects()[0].height / panesHeight;
            }
            else {
                collClassifier.style.background = "#8c8c8c";
                this.classifierRatio = 0;
            }

            if (page.getClientRects()[0]) {
                collPage.style.background = "white";
                this.pageRatio = page.getClientRects()[0].height / panesHeight;
            }
            else {
                collPage.style.background = "#8c8c8c";
                this.pageRatio = 0;
            }

            if (image.getClientRects()[0]) {
                collImage.style.background = "white";
                this.imageRatio = image.getClientRects()[0].height / panesHeight;
            }
            else {
                collImage.style.background = "#8c8c8c";
                this.imageRatio = 0;
            }

            this.rePosition();
        },

        rePosition: function () {
            var classifier = document.getElementById("right0");
            var page = document.getElementById("right1");
            var image = document.getElementById("right2");
            var collapsePane = document.getElementById("collapse-pane").getClientRects()[0];
            var classEdit = document.getElementById("left1");
            var glyphEdit = document.getElementById("left2");

            var imageZoomOut = document.getElementById("image-out");
            var imageZoomIn = document.getElementById("image-in");
            var space = 1; // this keeps the zoom buttons slightly below the image's top border

            if (classifier.getClientRects()[0]) {
                classifier.style.top = collapsePane.bottom + "px";
                if (page.getClientRects()[0]) {
                    page.style.top = classifier.getClientRects()[0].bottom + "px";
                    if (image.getClientRects()[0]) {
                        image.style.top = page.getClientRects()[0].bottom + "px";
                    }
                }
                else {
                    if (image.getClientRects()[0]) {
                        image.style.top = classifier.getClientRects()[0].bottom + "px";
                    }
                }
            }
            else {
                if (page.getClientRects()[0]) {
                    page.style.top = collapsePane.bottom + "px";
                    if (image.getClientRects()[0]) {
                        image.style.top = page.getClientRects()[0].bottom + "px";
                    }
                }
                else {
                    if (image.getClientRects()[0]) {
                        image.style.top = collapsePane.bottom + "px";
                    }
                }
            }

            if (image.getClientRects()[0]) {
                imageZoomOut.style.top = imageZoomIn.style.top = image.getClientRects()[0].top + space + "px";
            }
            glyphEdit.style.height = window.innerHeight - classEdit.getClientRects()[0].bottom + "px";
            glyphEdit.style.top = classEdit.getClientRects()[0].bottom + "px";
        },

        onMouseDown: function () {
            this.isMouseDown = true;
        },

        saveChanges: function (event) {
            if (event) {
                event.preventDefault();
            }
            RadioChannels.menu.trigger(MainMenuEvents.clickSaveChanges);
        },

        revertChanges: function (event) {
            if (event) {
                event.preventDefault();
            }
            RadioChannels.menu.trigger(MainMenuEvents.clickUndoAll);
        },

        zoomIn: function (event) {
            if (event) {
                event.preventDefault();
            }
            this.isZoomIn = true;
            this.zoomCount++;
            if (this.zoomCount < this.maxZoomCount) {
                RadioChannels.edit.trigger(GlyphEvents.zoomGlyphs, this.zoomLevel, this.isZoomIn);
            }
            else {
                this.zoomCount--;
            }
        },

        zoomOut: function (event) {
            if (event) {
                event.preventDefault();
            }
            this.isZoomIn = false;
            this.zoomCount--;
            if (this.zoomCount > -this.maxZoomCount) {
                RadioChannels.edit.trigger(GlyphEvents.zoomGlyphs, this.zoomLevel, this.isZoomIn);
            }
            else {
                this.zoomCount++;
            }
        },

        /**
         * Open the GlyphEditView for editing a particular glyph.
         *
         * @param {Glyph} model - A Glyph model.
         */
        openGlyphEdit: function (model) {
            this.glyphEditRegion.show(new GlyphEditView({
                model: model
            }));
        },

        /**
         * Open the GlyphMultiEditView for editing a particular collection of
         * Glyph models.
         *
         * @param {GlyphCollection} collection - Collection of glyphs to edit.
         */
        openMultiGlyphEdit: function (collection) {
            this.glyphEditRegion.show(new GlyphMultiEditView({
                collection: collection
            }));
        },

        /**
         * Open the TrainingEditView for editing a particular collection of
         * Training glyph models.
         *
         * @param {GlyphCollection} collection - Collection of training glyphs to edit.
         */
        openTrainingEdit: function (collection) {
            this.glyphEditRegion.show(new TrainingEditView({
                collection: collection
            }));
        },

        /**
         * Open the ClassEditView for editing a class.
         *
         * @param {String} className - a class name as a String
         */
        openClassEdit: function (className) {
            var model = new Class({
                name: className
            });
            this.glyphEditRegion.show(new ClassEditView({
                model: model
            }));

        },

        clearEditRegion: function () {
            this.glyphEditRegion.empty();
            var glyphRegion = document.getElementsByClassName("glyph-edit-region")[0];
            var editParagraph = document.createElement('p');
            editParagraph.innerHTML = Strings.editGlyphDescription;
            glyphRegion.replaceChildren(editParagraph);
        },

        /**
         * This template has lots of localized strings.
         *
         * @returns {{classesHeader: *, editGlyphLabel: (*|string), editGlyphDescription: (*|string)}}
         */
        serializeData: function () {
            return {
                classesHeader: Strings.classes,
                editGlyphLabel: Strings.editGlyphLabel,
                editGlyphDescription: Strings.editGlyphDescription,
                saveChanges: Strings.saveChanges,
                revert: Strings.undoAll,
                classifierGlyphs: Strings.classifierGlyphs,
                pageGlyphs: Strings.pageGlyphs,
                selectedGlyphs: Strings.selectedGlyphs
            }
        }
    });

export default RodanDashboardView;
