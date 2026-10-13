import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Password view.
 */
export default class ViewConfirmationDialog extends Marionette.CollectionView
{
    initialize(options)
    {
        this._message = options.message;
        this._onConfirm = options.onConfirm;
    }

    templateContext()
    {
        return {
            message: this._message
        };
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    _handleButtonConfirm()
    {
        this._onConfirm();
    }

    _handleButtonCancel()
    {
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }
    
}

ViewConfirmationDialog.prototype.modelEvents = {
            'all': 'render'
        };

ViewConfirmationDialog.prototype.ui = {
            buttonConfirm: '#button-confirm',
            buttonCancel: '#button-cancel'
        };

ViewConfirmationDialog.prototype.events = {
            'click @ui.buttonConfirm': '_handleButtonConfirm',
            'click @ui.buttonCancel': '_handleButtonCancel'
        };

ViewConfirmationDialog.prototype.template = _.template($('#template-dialog_confirm').text());
