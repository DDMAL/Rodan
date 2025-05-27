import Marionette from "marionette";
import template from "./confirm.template.html";

/**
 * @class ConfirmView
 *
 * A view which displays a message and a button for the user to click.  When they click the button, an arbitrary
 * callback function is called.
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
        // Trigger the button click callback!
        this.model.triggerCallback();
    }
});