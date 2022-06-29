import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * InputPort Collection Item view.
 */
export default class ViewInputPortCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflow' (Workflow) and 'options.workflowjob' (WorkflowJob) must also be provided
     */
    initialize(options)
    {
        this._workflow = options.workflow;
        this._workflowJob = options.workflowjob;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle delete.
     */
    _handleButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_INPUTPORT, {inputport: this.model, workflow: this._workflow, workflowjob: this._workflowJob});
    }
}
ViewInputPortCollectionItem.prototype.ui = {
            buttonDelete: '#button-delete'
        };
ViewInputPortCollectionItem.prototype.events = {
            'click @ui.buttonDelete': '_handleButtonDelete'
        };
ViewInputPortCollectionItem.prototype.template = _.template($('#template-main_inputport_collection_item').text());
ViewInputPortCollectionItem.prototype.tagName = 'tr';
