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

        this._minimum = this._getMinimumOutputPortCount();

        this._outputPorts = this._workflowJob.get("output_ports");
        this._outputPorts.on("change add remove reset", () => this._handleOutputPortsChange());
    }

    templateContext()
    {
        return {
            disableDelete: this._getCurrentOutputPortCount() <= this._minimum
        }
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

    _handleOutputPortsChange()
    {
        this.render(); // We need to re-render if the the job's output port changes to disable/enable delete button.
    }

    _getCurrentOutputPortCount()
    {
        return this._outputPorts.where({ output_port_type: this.model.get("output_port_type") }).length;
    }

    _getMinimumOutputPortCount()
    {
        const jobCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION);
        const outputPortTypes = jobCollection.get(this._workflowJob.getJobUuid()).get("output_port_types");

        const portTypeUrl = this.model.get("output_port_type");
        const portType = outputPortTypes.findWhere({url: portTypeUrl});

        return portType.get("minimum");
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
