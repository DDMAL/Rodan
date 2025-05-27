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
        
        this._minimum = this._getMinimumInputPortCount();

        this._inputPorts = this._workflowJob.get("input_ports");
        this._inputPorts.on("change add remove reset", () => this._handleInputPortsChange());
    }

    templateContext()
    {
        return {
            disableDelete: this._getCurrentInputPortCount() <= this._minimum
        };
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

    _handleInputPortsChange()
    {
        this.render(); // We need to re-render if the the job's input port changes to disable/enable delete button.
    }

    _getCurrentInputPortCount()
    {
        return this._inputPorts.where({ input_port_type: this.model.get("input_port_type") }).length;
    }

    _getMinimumInputPortCount()
    {
        const jobCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION);
        const inputPortTypes = jobCollection.get(this._workflowJob.getJobUuid()).get("input_port_types");

        const portTypeUrl = this.model.get("input_port_type");
        const portType = inputPortTypes.findWhere({url: portTypeUrl});

        return portType.get("minimum");
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
