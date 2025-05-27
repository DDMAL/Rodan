import BaseItem from './BaseItem';
import BaseWorkflowJobItem from './BaseWorkflowJobItem';
import GUI_EVENTS from '../Shared/Events';
import Radio from 'backbone.radio';
import Rodan from 'rodan';

/**
 * WorkflowJobGroup item.
 */
class WorkflowJobGroupItem extends BaseWorkflowJobItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        super(options);
        this._workflowJobUrls = options.model.get('workflow_jobs');
        var workflow = Radio.channel('rodan-client_gui').request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.menuItems = [{label: 'Edit', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOBGROUP_VIEW, options: {workflow: workflow, workflowjobgroup: this.getModel()}},
                          {label: 'Ungroup', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_UNGROUP_WORKFLOWJOBGROUP, options: {workflowjobgroup: this.getModel(), workflow: workflow}},
                          {label: 'Delete', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_WORKFLOWJOBGROUP, options: {workflow: workflow, workflowjobgroup: this.getModel()}}];

        this.coordinateSetInfo = [];
        this.coordinateSetInfo['url'] = 'workflow_job_group';
        this.loadCoordinates();
        this.fillColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].WORKFLOWJOBGROUP_FILL_COLOR;
        this._gotPorts = false;
    }

    /**
     * Update.
     */
    update()
    {
        // Make sure WorkflowJobItems are hidden.
        this._setWorkflowJobVisibility(false);

        // We need to get the associated ports.
        if (!this._gotPorts)
        {
            this._getAssociatedPorts();
        }

        super.update();
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        this._setWorkflowJobVisibility(true);
        var inputPortItems = this._paperGroupInputPorts.removeChildren();
        var outputPortItems = this._paperGroupOutputPorts.removeChildren();
        for (var index in inputPortItems)
        {
            inputPortItems[index].resetOwner();
        }
        for (var index in outputPortItems)
        {
            outputPortItems[index].resetOwner();
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
        var workflow = Radio.channel('rodan-client_gui').request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWJOBGROUP_VIEW, {workflowjobgroup: this.getModel(), workflow: workflow});
    }

    /**
     * Set visibility of associated WorkflowJobItems.
     */
    _setWorkflowJobVisibility(visible)
    {
        for (var index in this._workflowJobUrls)
        {
            var item = BaseItem.getAssociatedItem(this._workflowJobUrls[index]);
            if (item)
            {
                item.setVisible(visible);
            }
        }  
    }

    /**
     * Get associated ports.
     */
    _getAssociatedPorts()
    {
        var workflow = Radio.channel('rodan-client_gui').request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        var ports = this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWJOBGROUP_GET_PORTS, {url: this._modelURL, workflow: workflow});
        if (ports)
        {
            for (var index in ports.inputports)
            {
                var inputPortItem = BaseItem.getAssociatedItem(ports.inputports[index].get('url'));
                inputPortItem.setOwner(this._modelURL);
            }

            for (index in ports.outputports)
            {
                var outputPortItem = BaseItem.getAssociatedItem(ports.outputports[index].get('url'));
                outputPortItem.setOwner(this._modelURL);
            }
            this._gotPorts = true;
        }
    }
}

export default WorkflowJobGroupItem;
