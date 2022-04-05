import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

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
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_LOGIN, {username: this.ui.textUsername.val(), password: this.ui.textPassword.val()}); 
    }
}
ViewLogin.prototype.modelEvents = {
    'all': 'render'
};
ViewLogin.prototype.ui = {
    textUsername: '#text-login_username',
    textPassword: '#text-login_password',
    buttonLogin: '#button-login'
};
ViewLogin.prototype.events = {
    'click @ui.buttonLogin': '_handleButton'
};
ViewLogin.prototype.template = _.template($('#template-main_login').text());
