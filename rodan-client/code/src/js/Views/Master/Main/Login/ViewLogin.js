import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewForgotPassword from './ViewForgotPassword';
import ViewRegister from './ViewRegister';

/**
 * Login view.
 */
export default class ViewLogin extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_CLEAR);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle login button.
     */
    _handleButton()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_LOGIN, { email: this.ui.textEmail.val(), password: this.ui.textPassword.val() }); 
    }

    /**
     * Handle register button.
     */
    _handleButtonRegister()
    {
        const content = new ViewRegister();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, { title: 'Register', content });
    }

    /**
     * Handle forgot password button.
     */
    _handleButtonForgotPassword()
    {
        const content = new ViewForgotPassword();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, { title: 'Forgot Password', content });
    }
}
ViewLogin.prototype.modelEvents = {
    'all': 'render'
};
ViewLogin.prototype.ui = {
    textEmail: '#text-login_email',
    textPassword: '#text-login_password',
    buttonLogin: '#button-login',
    buttonRegister: '#button-register',
    buttonForgotPassword: '#button-forgot_password'
};
ViewLogin.prototype.events = {
    'click @ui.buttonLogin': '_handleButton',
    'click @ui.buttonRegister': '_handleButtonRegister',
    'click @ui.buttonForgotPassword': '_handleButtonForgotPassword'
};
ViewLogin.prototype.template = _.template($('#template-main_login').text());
