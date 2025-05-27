import Backbone from "backbone";
import GlyphEvents from "events/GlyphEvents";
import RadioChannels from "radio/RadioChannels";
import ClassNameUtils from "utils/ClassNameUtils";

/**
 * A Glyph object within the interactive classifier.
 *
 * @class Glyph
 */
export default Backbone.Model.extend(
    /**
     * @lends Glyph.prototype
     */
    {
        defaults: {
            id: 0,
            class_name: "",
            id_state_manual: false,
            confidence: 0.0,
            ulx: 0,
            uly: 0,
            nrows: 0,
            ncols: 0,
            image_file: "",
            image_b64: "",
            parts: [],
            split: {},
            is_training: false,
            width: 0,
            height: 0
        },

        initialize: function ()
        {
            this.set({
                width: this.get("ncols"),
                height: this.get("nrows")
            });

            this.listenTo(RadioChannels.edit, GlyphEvents.zoomGlyphs,
            function (zoomLevel, isZoomIn)
            {
                var oldWidth = this.get("width");
                var oldHeight = this.get("height");
                var newWidth, newHeight;
                if (isZoomIn)
                {
                    newWidth = oldWidth * zoomLevel;
                    newHeight = oldHeight * zoomLevel;
                }
                else
                {
                    if (oldWidth / zoomLevel > 1 && oldHeight / zoomLevel > 1)
                    {
                        newWidth = oldWidth / zoomLevel;
                        newHeight = oldHeight / zoomLevel;
                    }
                }
                this.set({
                    width: newWidth,
                    height: newHeight
                });
            });
        },
        /**
         * Creates a new glyph.
         *
         * @param {string} className - The name for the class.
         */
        onCreate: function ()
        {
            RadioChannels.edit.trigger(GlyphEvents.addGlyph, this, this.get("class_name"));
            RadioChannels.edit.trigger(GlyphEvents.setGlyphName, this.get("class_name"));
        },

        /**
         * Change the class of the glyph.
         *
         * This method fires events that might change the location where the
         * glyph is being rendered on the glyph table.
         *
         * @param {string} newClassName - The new name for the class.
         */
        changeClass: function (newClassName, isManual = true)
        {
            // Make sure it's a string
            newClassName = String(newClassName);
            // do the sanitization step
            var sanitizedClassName = ClassNameUtils.sanitizeClassName(newClassName);
            if (sanitizedClassName !== "" && sanitizedClassName !== "unclassified")
            {
                var oldClassName = this.get("class_name");
                var confidence = 1.0;
                var id_state_manual = true;
                // In case of grouping, we don't want the glyph to be manual
                if (!isManual)
                {
                    confidence = 0;
                    id_state_manual = false;
                } // TODO: this is redundant, should be fixed
                else
                {
                    confidence = 1.0;
                    id_state_manual = true;
                }
                this.set(
                {
                    class_name: sanitizedClassName,
                    id_state_manual: id_state_manual,
                    confidence: confidence
                });

                // Update glyph table location
                RadioChannels.edit.trigger(GlyphEvents.moveGlyph, this, oldClassName, this.get("class_name"));
                RadioChannels.edit.trigger(GlyphEvents.changeGlyph, this);
                RadioChannels.edit.trigger(GlyphEvents.setGlyphName, this.get("class_name"));
                
                // Deselect the glyph after changing its class
                // This is for the user's convenience so they can continue using arrow keys to navigate the page glyphs
                RadioChannels.edit.trigger(GlyphEvents.deselectGlyph, this);
            }
        },
        /**
         * Rename the glyph's name according to the user input
         *
         * This method moves the glyphs with this name from one row collection to a new row
         *
         * @param {string} renamedName - The renamed class.
         */
        renameGlyph: function (renamedName)
        {
            var oldClassName = this.get("class_name");
            renamedName = String(renamedName);
            var sanitizedName = ClassNameUtils.sanitizeClassName(renamedName);
            if (sanitizedName !== "unclassified" && sanitizedName !== "")
            {
                this.set('class_name', sanitizedName);

                RadioChannels.edit.trigger(GlyphEvents.moveGlyph, this, oldClassName, this.get("class_name"));
                RadioChannels.edit.trigger(GlyphEvents.changeGlyph, this);
                RadioChannels.edit.trigger(GlyphEvents.setGlyphName, this.get("class_name"));
            }
        },

        /**
         * Unclassify a glyph
         *
         * This method fires events that might change the location where the
         * glyph is being rendered on the glyph table.
         *
         *
         */
        unclassify: function ()
        {
            // Make sure it's a string

            var oldClassName = this.get("class_name");
            var newClassName = "UNCLASSIFIED";

            this.set({
                class_name: "UNCLASSIFIED",
                id_state_manual: false,
                confidence: 0
            });

            // Update glyph table location
            RadioChannels.edit.trigger(GlyphEvents.moveGlyph, this, oldClassName, newClassName);
            RadioChannels.edit.trigger(GlyphEvents.changeGlyph, this);
            //RadioChannels.edit.trigger(GlyphEvents.setGlyphName, newClassName);

        }
    });
