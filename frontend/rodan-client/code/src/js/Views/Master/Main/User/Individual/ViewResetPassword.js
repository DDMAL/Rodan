import Marionette from "backbone.marionette";
import Radio from "backbone.radio";
import $ from "jquery";
import RODAN_EVENTS from "js/Shared/RODAN_EVENTS";
import _ from "underscore";

/**
 * Password reset view.
 */
export default class ViewResetPassword extends Marionette.View {
    initialize(options) {
        this._uid = options.uid;
        this._token = options.token;
    }
    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle submit button.
     */
    _handleButtonSubmit() {
        var passwordError = this._checkPassword();
        if (passwordError) {
            this.ui.textMessage.text(passwordError);
        }
        else {
            Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__USER_RESET_PASSWORD_CONFIRM, { uid: this._uid, token: this._token, new_password: this.ui.textPassword.val() });
        }
    }

    /**
     * Checks password fields. Will provide error text if passwords no good, else null.
     */
    _checkPassword() {
        var password = this.ui.textPassword.val();
        var confirm = this.ui.textPasswordConfirm.val();
        if (!password) {
            return "Your password cannot be empty. Come on, you must have done this before.";
        }
        else if (password !== confirm) {
            return "Passwords do not match.";
        }
        return null;
    }
}
ViewResetPassword.prototype.modelEvents = {
    "all": "render"
};
ViewResetPassword.prototype.ui = {
    buttonSubmit: "#button-reset_password",
    textPassword: "#text-password",
    textPasswordConfirm: "#text-password_confirm",
    textMessage: "#text-message",
};
ViewResetPassword.prototype.events = {
    "click @ui.buttonSubmit": "_handleButtonSubmit"
};
ViewResetPassword.prototype.template = _.template($("#template-main_user_reset-password").text());
