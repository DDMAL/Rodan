import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * View for editing WorkflowJob.
 */
export default class ViewControlWorkflowJob extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflow' (Workflow) must also be provided
     */
    initialize(options)
    {
        this._workflow = options.workflow;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        this.model.set({'name': this.ui.textName.val()});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWJOB_SAVE, {workflowjob: this.model});
    }

    /**
     * Handle delete button.
     */
    _handleButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_WORKFLOWJOB, {workflowjob: this.model, workflow: this._workflow});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }
}
ViewControlWorkflowJob.prototype.template = _.template($('#template-main_workflowjob').text());
ViewControlWorkflowJob.prototype.ui = {
    buttonSave: '#button-save_workflowjob_data',
    buttonDelete: '#button-delete_workflowjob',
    textName: '#text-workflowjob_name'
};
ViewControlWorkflowJob.prototype.events = {
    'click @ui.buttonSave': '_handleButtonSave',
    'click @ui.buttonDelete': '_handleButtonDelete'
};
