import Marionette from "backbone.marionette";
import Radio from "backbone.radio";
import $ from "jquery";
import RODAN_EVENTS from "js/Shared/RODAN_EVENTS";
import _ from "underscore";

/**
 * Activation required view.
 */
export default class ViewActivationRequired extends Marionette.View {
    
    initialize(options) {
        this._email = options.email;
    }

    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle resend activation email.
     */
    _handleButtonSubmit() {
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__USER_RESEND_ACTIVATION, { email: this._email });
    }
}

ViewActivationRequired.prototype.modelEvents = {
    "all": "render"
};

ViewActivationRequired.prototype.ui = {
    buttonSubmit: "#button-resend_activation_email",
};

ViewActivationRequired.prototype.events = {
    "click @ui.buttonSubmit": "_handleButtonSubmit"
};

ViewActivationRequired.prototype.template = _.template($("#template-main_activation-required").text());
