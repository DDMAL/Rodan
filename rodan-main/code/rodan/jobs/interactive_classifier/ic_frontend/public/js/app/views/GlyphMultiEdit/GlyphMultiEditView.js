import Marionette from "marionette";
import GlyphMultiEditThumbnailList from "./GlyphMultiEditThumbnailList";
import RadioChannels from "radio/RadioChannels";
import GlyphEvents from "events/GlyphEvents";
import Strings from "localization/Strings";
import template from "views/GlyphMultiEdit/glyph-multi-edit.template.html";
import ClassNameUtils from "utils/ClassNameUtils";
import ClassEvents from "events/ClassEvents";

export default Marionette.LayoutView.extend(
    /**
     * @lends GlyphMultiEditView.prototype
     */
    {
        template,

        regions: {
            thumbnailListRegion: ".thumbnail-list"
        },

        ui: {
            classInput: 'input[title="glyph-class"]'
        },

        events: {
            "submit": "onSubmitForm",
            "click .group": "group",
            "click #delete": "delete"
        },

        /**
         * @class GlyphMultiEditView
         *
         * This is the view that allows the user to set the class name of multiple
         * Glyph models at the same time.
         *
         * @constructs
         */
        initialize: function ()
        {
            // Set up an event listener so that when the user clicks on a class name
            // in the ClassTreeView, this view automatically populates its form with
            // that class name and submits the form.
            var that = this;
            this.listenTo(RadioChannels.edit, GlyphEvents.clickGlyphName,
                function (className)
                {
                    that.ui.classInput.val(className);
                    that.onSubmitForm();
                }
            );
        },

        /**
         * We also show a list of thumbnails of all the glyphs currently selected.
         */
        onShow: function ()
        {
            this.thumbnailListRegion.show(new GlyphMultiEditThumbnailList({
                collection: this.collection
            }));

            this.ui.classInput.focus();

            /**
             * If all selected glyphs have the same class name,
             * The class name will show up in the input box
             */
            var sameName = true;
            var glyphs = this.collection.models;
            for (var i = 0; i < glyphs.length - 1; i++)
            {
                // If all the glyphs have the same glyph name, then show that name in the text box
                if (glyphs[i].get('class_name') !== glyphs[i + 1].get('class_name'))
                {
                    sameName = false;
                }
            }
            if (sameName && glyphs.length > 0)
            {
                // Show the name in the text box if all glyphs are the same
                this.ui.classInput.val(glyphs[0].get('class_name'));
            }
            this.ui.classInput.select();
        },

        /**
         * When we submit the form, we take the class name from the form and set all of the glyphs to that class name.
         *
         * @param event
         */
        onSubmitForm: function (event)
        {
            if (event)
            {
                event.preventDefault();
            }
            var that = this;
            var className = this.ui.classInput.val();
            if (ClassNameUtils.sanitizeClassName(className) === "unclassified")
            {
                RadioChannels.edit.trigger(ClassEvents.invalidClass, Strings.unclassifiedClass);
            }
            else if (ClassNameUtils.sanitizeClassName(className) === "")
            {
                var message = className + Strings.invalidClass;
                RadioChannels.edit.trigger(ClassEvents.invalidClass, message);
            }
            else
            {
                this.collection.each(function (model)
                {
                    model.changeClass(that.ui.classInput.val());
                });
            }
        },

        /**
         * Group the selected glyphs into one
         *
         * @param event
         */
        group(event)
        {
            if (event)
            {
                event.preventDefault();
            }
            var that = this;
            var className = that.ui.classInput.val();
            if (ClassNameUtils.sanitizeClassName(className) === "unclassified")
            {
                RadioChannels.edit.trigger(ClassEvents.invalidClass, Strings.unclassifiedClass);
            }
            else if (ClassNameUtils.sanitizeClassName(className) === "")
            {
                var message = className + Strings.invalidClass;
                RadioChannels.edit.trigger(ClassEvents.invalidClass, message);
            }
            else
            {
                var glyphs = []
                this.collection.each(function (model)
                {
                    model.changeClass("_group._part." + className, false);
                    glyphs.push(model);
                });
                RadioChannels.edit.trigger(GlyphEvents.groupGlyphs, glyphs, className);
            }
        },

        /**
         * Delete all selected glyphs and trigger event
         *
         * @param event
         */
        delete(event)
        {
            if (event)
            {
                event.preventDefault();
            }
            var glyphs = []
            this.collection.each(function (model)
            {
                glyphs.push(model);
            });
            RadioChannels.edit.trigger(GlyphEvents.deleteConfirm, glyphs);
        },

        /**
         * Include some localized strings.
         *
         * @returns {{}}
         */
        serializeData: function ()
        {
            let output = {};
            output.gui = Strings.glyphMultiEdit;
            return output;
        }
    });
