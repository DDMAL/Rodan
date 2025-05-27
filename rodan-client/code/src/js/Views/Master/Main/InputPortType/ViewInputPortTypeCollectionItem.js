import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * InputPortType Collection item view.
 */
export default class ViewInputPortTypeCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflowjob' (WorkflowJob) and 'options.workflow' (Workflow) must also be provided
     */
    initialize(options)
    {
        this._workflowJob = options.workflowjob;
        this._workflow = options.workflow;
        this._inputPorts = this._workflowJob.get("input_ports");
        this._inputPorts.on("change add remove reset", () => this._handleInputPortsChange());
    }

    templateContext() 
    {
        return {
            current: this._getCurrentInputPortCount()
        };
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles input port add.
     */
    _handleButtonNewInputPort()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_ADD_INPUTPORT, {inputporttype: this.model, workflowjob: this._workflowJob, workflow: this._workflow});
    }

    _handleInputPortsChange()
    {
        this.render(); // We need to re-render if the the job's input port changes to update the current count.
    }

    _getCurrentInputPortCount()
    {
        return this._inputPorts.where({ input_port_type: this.model.get("url") }).length;
    }
}
ViewInputPortTypeCollectionItem.prototype.tagName = 'tr';
ViewInputPortTypeCollectionItem.prototype.template = _.template($('#template-main_inputporttype_collection_item').text());
ViewInputPortTypeCollectionItem.prototype.events = {
    'click @ui.buttonNewInputPort': '_handleButtonNewInputPort'
};
ViewInputPortTypeCollectionItem.prototype.ui = {
    buttonNewInputPort: '#button-new_inputport'
};
