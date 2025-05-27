import Marionette from "marionette";
import RadioChannels from "radio/RadioChannels";
import GlyphEvents from "events/GlyphEvents";
import ClassEvents from "events/ClassEvents";
import Strings from "localization/Strings";
import template from "./glyph-edit.template.html";
import ClassNameUtils from "utils/ClassNameUtils";

export default Marionette.ItemView.extend(
    /**
     * @lends GlyphEditView.prototype
     */
    {
        template,

        ui: {
            classInput: 'input[title="glyph-class"]',
            manualConfirmButton: '.manual-confirm-button'
        },

        events: {
            "submit": "onSubmitForm",
            "click .split": "split",
            "click #delete": "delete"
        },

        modelEvents: {
            "change": "render"
        },

        /**
         * @class GlyphEditView
         *
         * This view is created when a user clicks on an individual glyph.  This view allows the user to set the class name of
         * that glyph.
         *
         * @constructs
         */
        initialize: function ()
        {
            // Set up an event listener.  When a user clicks on a class name in the
            // ClassTreeView, this view form becomes populated with that name and
            // the form is submitted.
            var that = this;
            this.listenTo(RadioChannels.edit, GlyphEvents.clickGlyphName,
                function (className)
                {
                    if (ClassNameUtils.sanitizeClassName(className) !== "unclassified" &&
                       ClassNameUtils.sanitizeClassName(className) !== "")
                    {
                        that.ui.classInput.val(className);
                        that.onSubmitForm();
                    }
                }
            );
        },

        /**
         * We "focus" on the input element so that the user can immediately type without having to click on the form
         * element.
         */
        onShow: function ()
        {
            // Automatically focus on the glyph class input and hightlight the text
            this.ui.classInput.focus();
            this.ui.classInput.select();
        },

        /**
         * When the user submits the form, we change the class of the glyph model.
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
                this.model.changeClass(this.ui.classInput.val());
            }

        },

        /**
         * When the user clicks here, the glyph will be split according to the option selected.
         *
         * @param event
         */
        split: function (event)
        {
            if (event)
            {
                event.preventDefault();
            }
            var selection = document.getElementById("split_option");
            var val = "";
            switch (selection.value)
            {
                case "Split x":
                    val = "splitx";
                    break;
                case "Split x left":
                    val = "splitx_left";
                    break;
                case "Split x right":
                    val = "splitx_right";
                    break;
                case "Split x max":
                    val = "splitx_max";
                    break;
                case "Split y":
                    val = "splity";
                    break;
                case "Split y bottom":
                    val = "splity_bottom";
                    break;
                case "Split y top":
                    val = "splity_top";
                    break;
            }
            // False meaning isManual is false
            this.model.changeClass("_split." + val, false);
            RadioChannels.edit.trigger(GlyphEvents.splitGlyph, this.model, val);
        },

        delete: function(event)
        {
            if (event)
            {
                event.preventDefault();
            }
            var glyph = [this.model];
            RadioChannels.edit.trigger(GlyphEvents.deleteGlyphs, glyph);
        },

        /**
         * Include model data and also localized strings for form labels.
         *
         * @returns {*|string}
         */
        serializeData: function ()
        {
            // Get the model fields
            var output = this.model.toJSON();
            // Add strings for the localized GUI.
            output.gui = Strings.editGlyph;
            return output;
        }
    });
