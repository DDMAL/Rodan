import $ from "jquery";
import Marionette from "marionette";
import GlyphTableRowView from "views/GlyphTable/Row/GlyphTableRowView";
import GlyphEvents from "events/GlyphEvents";
import RadioChannels from "radio/RadioChannels";

/**
 * @class GlyphTableView
 *
 * This view is the main GUI where all of the glyphs are and ordanized by class.
 *
 * This view also handles logic for selecting glyphs to be edited.  Right now,
 * there are two ways that users can select glyphs:
 *
 *      - The first way is to click on an individual glyph.  This causes the
 *        GlyphEditView to open.
 *
 *      - The second way is to click and drag.  This causes a blue "lasso" box
 *        to appear.  Glyphs which collide with the lasso box will be
 *        selected.  These glyphs are sent to the GlyphMultiEditView.
 *
 *  It is important to note that each individual GlyphTableItemView in the table
 *  has event listeners which listen to the dragSelect event.  This event is
 *  fired when the user comples a click and drag selection.
 *
 *  So, it is the GlyphTableView which triggers the click and drag selection,
 *  but it is the individual GlyphTableItemViews which determine whether or not
 *  they have been selected.
 *
 *  @constructs GlyphTableView
 */
export default Marionette.CollectionView.extend(
    /**
     * @lends GlyphTableView.prototype
     */
    {
        tagName: 'table',
        className: "table table-hover",
        childView: GlyphTableRowView,

        isMouseDown: false,
        mouseDownX: 0,
        mouseDownY: 0,

        /**
         * selectionBox is the blue lasso that appears when the user clicks and
         * drags their mouse.
         */
        selectionBox: undefined,

        resizeEvent: undefined,

        ui: {
            "selectionBox": ".selection-box"
        },

        events: {
            "mousedown": "onMouseDown"
        },

        initialize: function ()
        {
            // This waits for the preview image to load before retrieving its height
            var renderTime = 1000;
            setTimeout(function()
            {
                var pic = document.getElementsByClassName("preview-background")[0];
                var h = pic.getClientRects()[0].height;
                if (h !== 0)
                {
                    pic.dataset.originalHeight = h;
                }
            }, renderTime);
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
            event.preventDefault();
            this.isMouseDown = true;
            this.mouseDownX = event.clientX;
            this.mouseDownY = event.clientY;

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
                    var boundingBox = {
                        left: Math.min(that.mouseDownX, x),
                        top: Math.min(that.mouseDownY, y),
                        right: Math.max(that.mouseDownX, x),
                        bottom: Math.max(that.mouseDownY, y)
                    };

                    // If the user holds shift, then this selection is an additional selection
                    var isAdditional = event.shiftKey === true;

                    if (!isAdditional)
                    {
                        // Deselects all the previously selected glyphs
                        RadioChannels.edit.trigger(GlyphEvents.deselectAllGlyphs);
                    }

                    // This is the event that triggers the GlyphMultiEditView to be
                    // opened.  This event is also listened to by GlyphTableItemView
                    // views, which check whether or not they collide with
                    // boundingBox.
                    RadioChannels.edit.trigger(
                        GlyphEvents.dragSelect,
                        boundingBox,
                        isAdditional, // If the shift key is held, then it's an "additional" selection!
                        this.collection.is_classifier
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
            var that = this;
            //trigger mousemove only if mouse is down
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
                    return;
                }
                else
                {
                    var x = event.pageX,
                    y = event.pageY;
                    that.selectionBox.style.left = Math.min(x, that.mouseDownX) + "px";
                    that.selectionBox.style.top = Math.min(y, that.mouseDownY) + "px";
                    that.selectionBox.style.width = Math.abs(x - that.mouseDownX) + "px";
                    that.selectionBox.style.height = Math.abs(y - that.mouseDownY) + "px";
                }
            });
        }
    });
