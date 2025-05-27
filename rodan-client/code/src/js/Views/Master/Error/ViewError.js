import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Error view.
 */
export default class ViewError extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button.
     */
    _handleButton()
    {
       // Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_LOGIN, {username: this.ui.textUsername.val(), password: this.ui.textPassword.val()}); 
    }
}
ViewError.prototype.ui = {
    buttonSendError: '#button-send_error'
};
ViewError.prototype.events = {
    'click @ui.buttonSendError': '_handleButton'
};