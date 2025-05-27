import BaseWorkflowJobItem from './BaseWorkflowJobItem';
import GUI_EVENTS from '../Shared/Events';
import Radio from 'backbone.radio';
import Rodan from 'rodan';

/**
 * WorkflowJob item.
 */
class WorkflowJobItem extends BaseWorkflowJobItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC STATIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns context menu data for multiple items of this class.
     * Takes in URLs of multiple selections.
     *
     * The menu data is simply an array of objects. Objects should be:
     *
     * {
     *      label: [string] // The text that should appear
     *      radiorequest: Rodan.RODAN_EVENTS.?  // The Request to make. NOT A RADIO EVENT, rather a REQUEST.
     *      options: Object holding any options for Event
     * }
     */
    static getContextMenuDataMultiple()
    {
        var workflowJobs = Radio.channel('rodan-client_gui').request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_SELECTED_WORKFLOWJOBS);
        var workflow = Radio.channel('rodan-client_gui').request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        return [{channel: 'rodan', label: 'Group', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_ADD_WORKFLOWJOBGROUP, options: {workflowjobs: workflowJobs, workflow: workflow}}];
    }

///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        super(options);
        var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.menuItems = [{label: 'Edit', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOB_VIEW, options: {workflowjob: this.getModel(), workflow: workflow}},
                          {label: 'Settings', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOB_SETTINGS_VIEW, options: {workflowjob: this.getModel(), workflow: workflow}},
                          {label: 'Ports', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOB_PORTS_VIEW, options: {workflowjob: this.getModel(), workflow: workflow}},
                          {label: 'Delete', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_WORKFLOWJOB, options: {workflowjob: this.getModel(), workflow: workflow}}];
        var model = this.getModel();
        if (!model.hasSettings())
        {
            this.menuItems.splice(1, 1); 
        }
        this.coordinateSetInfo = [];
        this.coordinateSetInfo['url'] = 'workflow_job';
        this.loadCoordinates();
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        var inputPortItems = this._paperGroupInputPorts.removeChildren();
        var outputPortItems = this._paperGroupOutputPorts.removeChildren();
        for (var index in inputPortItems)
        {
            var port = inputPortItems[index];
            port.destroy();
        }
        for (index in outputPortItems)
        {
            port = outputPortItems[index];
            port.destroy();
        }
        super.destroy();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle double click.
     */
    _handleDoubleClick(mouseEvent)
    {
        var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOB_VIEW, {workflowjob: this.getModel(), workflow: workflow});
    }
}

export default WorkflowJobItem;