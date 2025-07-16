import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * Project admin view.
 */
export default class ViewDeleteConfirm extends Marionette.View {
    ///////////////////////////////////////////////////////////////////////////////////////
    // PUBLIC METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object;
     */
    initialize(options) {
        this._type = options.type;
        this._names = options.names;
        this._toDelete = options.toDelete;
        this.setElement('<div id="delete-confirm-modal-body-wrapper" class="content-wrapper column-content flex-gap-10"></div>');
    }

    /**
     * Serialize data to be passed to the template.
     *
     * @returns {object} Data to be used in the template.
     */
    serializeData() {
        return {
            type: this._type,
            names: this._names
        };
    }

    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button cancel delete.
     */
    _handleCancelDelete() {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }

    /**
     * Handle button confirm delete.
     */
    _handleConfirmDelete() {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);

        switch (this._type) {
            case 'project':
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_DELETE, { project: this._toDelete });
                break;
            case 'resource':
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_DELETE, { resource: this._toDelete });
                break;
            case 'workflow':
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_DELETE, { workflow: this._toDelete });
                break;
            default:
                throw new Error('Invalid type: ' + this._type);
        }
    }
}

ViewDeleteConfirm.prototype.template = _.template($('#template-main_shared_delete_confirm').text());
ViewDeleteConfirm.prototype.ui = {
    buttonCancelDelete: '#button-cancel_delete',
    buttonConfirmDelete: '#button-confirm_delete'
};
ViewDeleteConfirm.prototype.events = {
    'click @ui.buttonCancelDelete': '_handleCancelDelete',
    'click @ui.buttonConfirmDelete': '_handleConfirmDelete'
};
