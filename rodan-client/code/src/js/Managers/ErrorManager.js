import Backbone from 'backbone';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * General error manager.
 */
export default class ErrorHandler
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor()
    {
        window.onerror = (errorText, url, lineNumber, columnNumber, error) => this._handleJavaScriptError(errorText, url, lineNumber, columnNumber, error);
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, (options) => this._handleError(options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles Javscript error.
     */
    _handleJavaScriptError(errorText, url, lineNumber, columnNumber, error)
    {
        var text = 'Rodan Client has encountered an unexpected error.<br><br>';
        text += 'text: ' + errorText + '<br>';
        text += 'url: ' + url + '<br>';
        text += 'line: ' + lineNumber + '<br>';
        text += 'column: ' + columnNumber;
        this._showError(text, error);
    }

    /**
     * Handle error.
     */
    _handleError(options)
    {
        var response = options.response;
        var responseTextObject = response.responseText !== '' ? JSON.parse(response.responseText) : null;
        if (responseTextObject !== null)
        {
            if (responseTextObject.hasOwnProperty('error_code'))
            {
                var error = options.response.responseJSON
                var text = error.error_code + '<br>';
                text += error.details[0];
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_ERROR, {json: error});
            }
            else
            {
                var message = options.message || 'An unknown error occured.';
                this._showError(message, null);
            }
        }
        else
        {
            this._showError(response.statusText, null);
        }
    }

    /**
     * Show error.
     */
    _showError(text, error)
    {
        if (error) {
            console.error(error);
        }
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, {content: text});
    }
}