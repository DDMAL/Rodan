import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Workflow Collection item for importing into another Workflow.
 */
export default class ViewWorkflowCollectionImportItem extends BaseViewCollectionItem
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
    _handleButtonImportWorkflow()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_IMPORT_WORKFLOW, {origin: this.model, target: this._workflow});
    }
}
ViewWorkflowCollectionImportItem.prototype.template = _.template($('#template-main_workflowbuilder_workflow_collection_item_import').text());
ViewWorkflowCollectionImportItem.prototype.tagName = 'tr';
ViewWorkflowCollectionImportItem.prototype.ui = {
    buttonImportWorkflow: '#button-main_workflowbuilder_workflow_import'
};
ViewWorkflowCollectionImportItem.prototype.events = {
    'click @ui.buttonImportWorkflow': '_handleButtonImportWorkflow',
    'dblclick': '_handleButtonImportWorkflow'
};
