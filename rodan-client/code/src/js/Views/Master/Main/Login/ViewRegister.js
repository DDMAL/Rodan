import Marionette from "backbone.marionette";
import Radio from "backbone.radio";
import $ from "jquery";
import RODAN_EVENTS from "js/Shared/RODAN_EVENTS";
import _ from "underscore";

/**
 * Forgot password view.
 */
export default class ViewRegister extends Marionette.View {
    initialize() {
        Radio.channel("rodan").on(RODAN_EVENTS.EVENT__USER_REGISTER_ERROR, options => this._handleRegisterError(options));
    }
    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle register button.
     */
    _handleButtonRegister() {
        const valid = this._validateFields();
        if (valid) {
            Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__USER_REGISTER, {
                username: this.ui.textUsername.val(),
                email: this.ui.textEmail.val(),
                password: this.ui.textPassword.val(),
            });
        }
    }

    /**
     * Validate all fields.
     */
    _validateFields() {
        this._validateUsername();
        this._validateEmail();
        this._validatePassword();
        this._validatePasswordConfirm();
        return this.ui.errorUsername.text() === "" && this.ui.errorEmail.text() === "" && this.ui.errorPassword.text() === "" && this.ui.errorPasswordConfirm.text() === "";
    }

    /**
     * Validate username.
     */
    _validateUsername() {
        const username = this.ui.textUsername.val();
        if (username === "") {
            this.ui.errorUsername.text("Username cannot be empty.");
        } else {
            this.ui.errorUsername.text("");
        }
    }

    /**
     * Validate email.
     */
    _validateEmail() {
        const email = this.ui.textEmail.val();
        if (email === "") {
            this.ui.errorEmail.text("Email cannot be empty.");
        } else if (!/^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/.test(email)) {
            this.ui.errorEmail.text("Invalid email.");
        } else {
            this.ui.errorEmail.text("");
        }
    }

    /**
     * Validate password.
     */
    _validatePassword() {
        const password = this.ui.textPassword.val();
        if (password === "") {
            this.ui.errorPassword.text("Password cannot be empty.");
        } else {
            this.ui.errorPassword.text("");
        }
    }

    /**
     * Validate password confirm.
     */
    _validatePasswordConfirm() {
        const password = this.ui.textPassword.val();
        const passwordConfirm = this.ui.textPasswordConfirm.val();
        if (password !== passwordConfirm) {
            this.ui.errorPasswordConfirm.text("Passwords do not match.");
        } else {
            this.ui.errorPasswordConfirm.text("");
        }
    }

    /**
     * Handle errors returned from server.
     * @param {{errors: {[string]: string[]}}} options map from field name to error messages
     */
    _handleRegisterError(options) {
        const errorMap = options.errors;
        for (const [key, errors] of Object.entries(errorMap)) {
            if (key === "username") {
                this.ui.errorUsername.text(errors.join(" "));
            } else if (key === "email") {
                this.ui.errorEmail.text(errors.join(" "));
            } else if (key === "password") {
                this.ui.errorPassword.text(errors.join(" "));
            } else if (key === "password_confirm") {
                this.ui.errorPasswordConfirm.text(errors.join(" "));
            }
        }
    }
}

ViewRegister.prototype.modelEvents = {
    "all": "render"
};

ViewRegister.prototype.ui = {
    buttonRegister: "#button-register",
    textUsername: "#text-username",
    textEmail: "#text-email",
    textPassword: "#text-password",
    textPasswordConfirm: "#text-password_confirm",
    errorUsername: "#error-username",
    errorEmail: "#error-email",
    errorPassword: "#error-password",
    errorPasswordConfirm: "#error-password_confirm"
};

ViewRegister.prototype.events = {
    "click @ui.buttonRegister": "_handleButtonRegister"
};

ViewRegister.prototype.template = _.template($("#template-main_register").text());
