//import Backbone from "backbone";
import Marionette from "marionette";
import Strings from "localization/Strings";
import ClassEvents from "events/ClassEvents";
import RadioChannels from "radio/RadioChannels";
import template from "./class-edit.template.html";
import ClassNameUtils from "utils/ClassNameUtils"
/**
 * The detailed class view
 */
export default Marionette.ItemView.extend({
    template,

    ui: {
        classInput: 'input[title="class-name"]',
        manualConfirmButton: '.manual-confirm-button'
    },

    events: {
        "click #delete": "delete",
        "submit": "onSubmitForm"
    },

    modelEvents: {
        "change": "render"
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
        output.gui = Strings.editClass;
        return output;
    },

    onSubmitForm: function(event)
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
        //trigger renameClass event with parameters (old name, new name)
        else
        {
            RadioChannels.edit.trigger(ClassEvents.renameClass, this.model.get("name"), className);
        }
    },

    delete: function(event)
    {
        if (event)
        {
            event.preventDefault();
        }
        RadioChannels.edit.trigger(ClassEvents.deleteClass, this.model.get("name"));
    }
});
