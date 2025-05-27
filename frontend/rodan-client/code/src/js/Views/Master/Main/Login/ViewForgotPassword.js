import Marionette from "backbone.marionette";
import Radio from "backbone.radio";
import $ from "jquery";
import RODAN_EVENTS from "js/Shared/RODAN_EVENTS";
import _ from "underscore";

/**
 * Forgot password view.
 */
export default class ViewForgotPassword extends Marionette.View {
    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSubmit() {
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__USER_RESET_PASSWORD, { email: this.ui.textEmail.val() });
    }
}
ViewForgotPassword.prototype.modelEvents = {
    "all": "render"
};
ViewForgotPassword.prototype.ui = {
    buttonSubmit: "#button-request_password_reset",
    textEmail: "#text-email",
    textMessage: "#text-message",
};
ViewForgotPassword.prototype.events = {
    "click @ui.buttonSubmit": "_handleButtonSubmit"
};
ViewForgotPassword.prototype.template = _.template($("#template-main_forgot-password").text());
