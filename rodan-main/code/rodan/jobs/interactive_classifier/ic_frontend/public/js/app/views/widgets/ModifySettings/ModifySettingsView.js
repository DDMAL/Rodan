import Marionette from "marionette";
import template from "./modifySettings.template.html";

/**
 * @class ModifySettingsView
 *
 * A view which displays a message, a list of settings for the users to edit, and a confirm button for the user to click.  When they click the button, an arbitrary
 * callback function is called.
 *
 *
 */
export default Marionette.ItemView.extend({
    template,

    ui: {
        button: ".btn"

    },

    events: {
        "click @ui.button": "onClickButton"

    },

    onClickButton: function ()
    {

        var userOptions = document.getElementsByClassName("userOption");
        var userArgs = {}
        //for (var option in userOptions)
        for (var i = 0; i < userOptions.length; i++)
        {
            var name = userOptions[i].name;
            var val = userOptions[i].value;

            // Checkbox's value cannot be accessed with .value
            if (userOptions[i].type === "checkbox")
            {
                val = userOptions[i].checked;
            }
            if (name !== undefined && val !== undefined)
            {
                userArgs[name] = val;
            }
        }

        // Trigger the button click callback!
        this.model.triggerCallback(userArgs);

    }

});