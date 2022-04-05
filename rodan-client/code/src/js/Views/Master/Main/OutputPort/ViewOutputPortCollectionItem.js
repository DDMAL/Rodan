import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * OutputPort Collection item view.
 */
export default class ViewOutputPortCollectionItem extends BaseViewCollectionItem
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
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_OUTPUTPORT, {outputport: this.model, workflow: this._workflow, workflowjob: this._workflowJob});
    }
}
ViewOutputPortCollectionItem.prototype.ui = {
    buttonDelete: '#button-delete'
};
ViewOutputPortCollectionItem.prototype.events = {
    'click @ui.buttonDelete': '_handleButtonDelete'
};
ViewOutputPortCollectionItem.prototype.template = _.template($('#template-main_outputport_collection_item').text());
ViewOutputPortCollectionItem.prototype.tagName = 'tr';
