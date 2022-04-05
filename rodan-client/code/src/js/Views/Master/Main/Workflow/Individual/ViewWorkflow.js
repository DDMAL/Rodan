import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Workflow view.
 */
export default class ViewWorkflow extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button run workflow.
     */
    _handleButtonRunWorkflow()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_CREATE_WORKFLOWRUN, {workflow: this.model});
    }

    /**
     * Handle button delete workflow.
     */
    _handleButtonDeleteWorkflow()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_DELETE, {workflow: this.model});
    }

    /**
     * Handle button edit workflow.
     */
    _handleButtonEditWorkflow()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWBUILDER_SELECTED, {workflow: this.model});
    }

    /**
     * Handle button copy workflow.
     */
    _handleButtonCopyWorkflow()
    {
    }

    /**
     * Handle button export workflow.
     */
    _handleButtonExport()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_EXPORT, {workflow: this.model});
    }

    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_SAVE, {workflow: this.model, fields: {name: _.escape(this.ui.textName.val()), description: _.escape(this.ui.textDescription.val())}});
    }
}
ViewWorkflow.prototype.modelEvents = {
            'all': 'render'
        };
ViewWorkflow.prototype.ui = {
    runWorkflowButton: '#button-run_workflow',
    deleteWorkflowButton: '#button-delete_workflow',
    copyWorkflowButton: '#button-copy_workflow',
    exportWorkflowButton: '#button-export_workflow',
    editWorkflowButton: '#button-edit_workflow',
    buttonSaveData: '#button-save_workflow_data',
    buttonSave: '#button-save_workflow',
    textName: '#text-workflow_name',
    textDescription: '#text-workflow_description'
        };
ViewWorkflow.prototype.events = {
    'click @ui.runWorkflowButton': '_handleButtonRunWorkflow',
    'click @ui.deleteWorkflowButton': '_handleButtonDeleteWorkflow',
    'click @ui.editWorkflowButton': '_handleButtonEditWorkflow',
    'click @ui.copyWorkflowButton': '_handleButtonCopyWorkflow',
    'click @ui.buttonSaveData': '_handleButtonSave',
    'click @ui.buttonSave': '_handleButtonSave',
    'click @ui.exportWorkflowButton': '_handleButtonExport'
        };
ViewWorkflow.prototype.template = _.template($('#template-main_workflow_individual').text());
