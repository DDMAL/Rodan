import $ from "jquery";
import Marionette from "marionette";
import GlyphEvents from "events/GlyphEvents";
import PageEvents from "events/PageEvents";
import template from "./image-preview.template.html";
import RadioChannels from "radio/RadioChannels";
// import GlyphCollection from "collections/GlyphCollection";

/**
 * @class ImagePreviewView
 *
 * This view displays the preview of the entire document page at the bottom right of the window.
 *
 * Calling highlightGlyph() draws a red highlight box over a particular glyph on the page.
 *
 * @constructs ImagePreviewView
 */
export default Marionette.ItemView.extend(
    /**
     * @lends ImagePreviewView.prototype
     */
    {

        template,
        isMouseDown: false,
        mouseDownX: 0,
        mouseDownY: 0,
        zoomCount: 0,
        zoomLevel: 1.25,
        maxZoomCount: 11,
        isZoomIn: false,

        /**
         * selectionBox is the blue lasso that appears when the user clicks and
         * drags their mouse.
         */
        selectionBox: undefined,

        resizeEvent: undefined,

        events: {
            "mousedown": "onMouseDown",
            "click #image-in": "imageZoomIn",
            "click #image-out": "imageZoomOut"
        },

        ui: {
            "selectionBox": ".selection-box",
            highlight: ".preview-highlight"
        },

        /**
         * Draw highlight boxes over the particular Glyph models that are on the page.
         *
         * @param {Glyph} glyphs - A collection of Glyph models.
         */
        highlightGlyph: function (glyphs)
        {
            // Change the dimensions of our highlight box to match those of the
            // glyph.

            // Getting rid of all the previously selected glyphs
            var elems = document.getElementsByClassName("preview-highlight");
            while (elems.length > 0)
            {
                var elem = elems[0];
                elem.parentNode.removeChild(elem);
            }

            for (var i = 0; i < glyphs.length; i++)
            {
                var glyph = glyphs[i];
                var pic = document.getElementsByClassName("preview-background")[0];
                var zoomLevel = pic.getBoundingClientRect().height / pic.dataset.originalHeight;

                var top = (glyph.get("uly")) * zoomLevel;
                var left = (glyph.get("ulx")) * zoomLevel;
                var width = glyph.get("ncols") * zoomLevel;
                var height = glyph.get("nrows") * zoomLevel;

                // Creating a box for each glyph
                var el = document.body.appendChild(document.createElement("div"));
                el.style = "top: " + top + "px; left: " + left + "px; width: " + width + "px; height: " + height + "px";
                el.style.background = "#9b05d1";
                el.style.position = "absolute";
                el.style.opacity = 0.4;
                el.style.filter = "alpha(opacity=40)"; // IE8
                el.style.visibility = "visible";
                el.className = 'preview-highlight';
                this.el.appendChild(el);
            }

            if (glyphs.length > 0)
            {
                // Scroll to the highlight of the first selected glyph
                elems = document.getElementsByClassName("preview-highlight");

                // If the user selected the glyph from the preview image, the page won't shift
                // If the user is zooming, then it will stay scroll to the highlighted glyph
                if (!this.isHover)
                {
                    elems[0].scrollIntoView({block: "center", inline: "center"});
                }
            }
        },

        // Remove the highlight of previously selected glyphs
        unhighlightGlyphs: function ()
        {
            var elems = document.getElementsByClassName("preview-highlight");
            while (elems.length > 0)
            {
                var elem = elems[0];
                elem.parentNode.removeChild(elem);
            }
        },

        /**
         * This function fires when the user clicks and holds their mouse down.
         * We record the location of the user's mouse and trigger the selectionBox
         * lasso to appear.
         *
         * @param event jQuery event object.
         */
        onMouseDown: function (event)
        {

            this.ui.highlight.css({
                top: 0,
                left: 0,
                width: 0,
                height: 0
            });

            this.isMouseDown = true;
            this.mouseDownX = event.clientX;
            this.mouseDownY = event.clientY;

            event.preventDefault();
            this.selectionBox.style.top = this.mouseDownY + "px";
            this.selectionBox.style.left = this.mouseDownX + "px";
            this.selectionBox.style.width = "0px";
            this.selectionBox.style.height = "0px";
            this.selectionBox.style.visibility = "visible";
        },

        /**
         * This function fires when the user who has been clicking and dragging
         * finally releases their mouse.
         *
         * This function triggers the logic to select whichever glyphs in the table
         * collide with the selectionBox.
         *
         * @param event jQuery event object.
         */
        onMouseUp: function (event)
        {
            if (this.isMouseDown === true)
            {
                this.isMouseDown = false;
                var x = event.clientX,
                    y = event.clientY;

                var width = Math.abs(x - this.mouseDownX),
                    height = Math.abs(y - this.mouseDownY);

                var that = this;

                if (width !== 0 && height !== 0 && (width * height) > 10)
                {
                    // boundingBox is the dimensions of the drag selection.  We will
                    // use these dimensions to test whether or not individual glyphs
                    // have been selected.

                    var pageBounds = document.getElementsByClassName("preview-background")[0].getBoundingClientRect();
                    var boundingBox = {
                        left: Math.min(that.mouseDownX, x) - pageBounds.left,
                        top: Math.min(that.mouseDownY, y) - pageBounds.top,
                        right: Math.max(that.mouseDownX, x) - pageBounds.left,
                        bottom: Math.max(that.mouseDownY, y) - pageBounds.top
                    };

                    // If the user holds shift, then this selection is an additional selection
                    var isAdditional = event.shiftKey === true;

                    if (!isAdditional)
                    {
                        RadioChannels.edit.trigger(GlyphEvents.deselectAllGlyphs);
                    }

                    // This is the event that triggers the GlyphMultiEditView to be
                    // opened.  This event is also listened to by GlyphTableItemView
                    // views, which check whether or not they collide with
                    // boundingBox.
                    RadioChannels.edit.trigger(
                        GlyphEvents.previewSelect,
                        boundingBox,
                        isAdditional // If the shift key is held, then it's an "additional" selection!
                    );
                    RadioChannels.edit.trigger(GlyphEvents.openMultiEdit);
                }
            }

            // Delete the selection box from the DOM
            this.selectionBox.style.visibility = "hidden";
        },

        /**
         * After the view is rendered, this function automatically constructs
         * the selectionBox as a hidden DOM element.
         *
         * This function also sets up an event listener which resizes the
         * selectionBox when the user moves their mouse.
         */
        onShow: function ()
        {
            this.selectionBox = document.body.appendChild(document.createElement("div"));
            this.selectionBox.style.background = "#337ab7";
            this.selectionBox.style.position = "absolute";
            this.selectionBox.style.opacity = 0.4;
            this.selectionBox.style.filter = "alpha(opacity=40)"; // IE8
            this.selectionBox.style.visibility = "hidden";

            var imageZoomOut = document.getElementById("image-out");
            var imageZoomIn = document.getElementById("image-in");
            // The 'right' variable keeps the buttons from overlapping the scrollbar of the image
            var right = 15;
            imageZoomIn.style.right = right + "px";
            imageZoomOut.style.right = right + imageZoomIn.getClientRects()[0].width + "px";

            var pic = document.getElementsByClassName("preview-background")[0];
            var imageBox = document.getElementById("right2").getClientRects()[0];
            var that = this;
            $(document).keypress(function (event)
            {
                if (that.isHover)
                {
                    if (event.key === "=")
                    {
                        that.imageZoomIn();
                    }
                    else if (event.key === "-")
                    {
                        that.imageZoomOut();
                    }
                }
            });

            var mouseClick = false;
            $(document).mousedown(function ()
            {
                mouseClick = true;
            });
            $(document).mouseup(function (event)
            {
                mouseClick = false;
                that.onMouseUp(event);
            });
            $(document).mousemove(function (event)
            {
                if (mouseClick === false)
                {
                    that.isHover = (event.clientX > imageBox.left && event.clientY > imageBox.top);
                    return;
                }
                else
                {
                    this.mouseDownX = event.clientX;
                    this.mouseDownY = event.clientY;

                    // This makes sure that the height isn't stored before the image exists
                    // So it's not set to 0
                    if (pic.style.height === "" || pic.style.height === "0px")
                    {
                        pic = document.getElementsByClassName("preview-background")[0];
                        if (pic.getClientRects()[0])
                        {
                            var h = pic.getClientRects()[0].height;
                        }
                        // Don't assign the height if h==0
                        if (h !== 0)
                        {
                            pic.style.height = h + "px";
                            pic.dataset.originalHeight = h;
                        }
                    }
                    that.isHover = (event.clientX > imageBox.left && event.clientY > imageBox.top);

                    var x = event.pageX,
                        y = event.pageY;

                    that.selectionBox.style.left = Math.min(x, that.mouseDownX) + "px";
                    that.selectionBox.style.top = Math.min(y, that.mouseDownY) + "px";
                    that.selectionBox.style.width = Math.abs(x - that.mouseDownX) + "px";
                    that.selectionBox.style.height = Math.abs(y - that.mouseDownY) + "px";

                }
            });
        },

        imageZoomIn: function (event)
        {
            if (event)
            {
                event.preventDefault();
            }
            this.isZoomIn = true;
            this.zoomCount++;
            if (this.zoomCount < this.maxZoomCount)
            {
                RadioChannels.edit.trigger(PageEvents.zoom, this.zoomLevel, this.isZoomIn);
            }
            else
            {
                this.zoomCount--;
            }
        },

        imageZoomOut: function (event)
        {
            if (event)
            {
                event.preventDefault();
            }
            this.isZoomIn = false;
            this.zoomCount--;
            if (this.zoomCount > -this.maxZoomCount)
            {
                RadioChannels.edit.trigger(PageEvents.zoom, this.zoomLevel, this.isZoomIn);
            }
            else
            {
                this.zoomCount++;
            }
        }
    });
