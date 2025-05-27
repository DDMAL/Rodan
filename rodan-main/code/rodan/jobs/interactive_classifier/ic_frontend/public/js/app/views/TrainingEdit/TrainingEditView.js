import Marionette from "marionette";
import GlyphMultiEditThumbnailList from "views/GlyphMultiEdit/GlyphMultiEditThumbnailList";
import RadioChannels from "radio/RadioChannels";
import GlyphEvents from "events/GlyphEvents";
import Strings from "localization/Strings";
import template from "views/TrainingEdit/training-edit.template.html";
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
            "click #delete": "delete"
        },

        /**
         * @class TrainingEditView
         *
         * Allows users to change the class of training glyphs
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
                if (glyphs[i].get('class_name') !== glyphs[i + 1].get('class_name'))
                {
                    sameName = false;
                }
            }
            if (sameName && glyphs.length > 0)
            {
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
                    model.changeClass(className);
                });
            }

        },

        /**
         * Delete the training glyph
         *
         * @param event
         */
        delete: function (event)
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
            if (glyphs.length > 1)
            {
                RadioChannels.edit.trigger(GlyphEvents.deleteConfirm, glyphs);
            }
            else
            {
                RadioChannels.edit.trigger(GlyphEvents.deleteGlyphs, glyphs);
            }
        },

        /**
         * Include some localized strings.
         *
         * @returns {{}}
         *
         * TODO: This needs to be checked/rewritten
         *
         */
        serializeData: function ()
        {
            let output = {};
            output.gui = Strings.glyphMultiEdit;
            return output;
        }
    });
