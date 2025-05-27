import Backbone from "backbone";

/**
 * @class ModifySettingsViewModel
 *
 * The ViewModel for the ModifySettingsView.  When the user clicks on the button in the ModifySettingsView, the callback property
 * is called.
 */
export default Backbone.Model.extend(
    /**
     * @lends ModifySettingsViewModel.prototype
     */
    {
        /*
        *
        * userOptions is a dictionary. There are three possible types: checkbox, dropdown and input. {ie "type": "dropdown"}
        * For all of them, the attribute "text" must be provided. (Text is the option name, ie "number of iterations")
        * For the type "input", the user is able to type what they want. A "default" attribute is required.
        * For the type "dropdown", the attribute "options" must be provided with a list of options. (ie "options": ["opt1", "opt2"])
        */
        defaults: {
            text: "",
            warning: undefined,
            buttonText: "Confirm",
            userOptions: {},
            callback: function ()
            {
                // Empty function
            }
        },

        /**
         * Trigger the callback function with the arguments the user provided.
         */
        triggerCallback: function (userArgs)
        {
            this.get("callback")(userArgs);
        }
    });