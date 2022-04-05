import $ from 'jquery';
import _ from 'underscore';
import GUI_EVENTS from '../Shared/Events';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import Rodan from 'rodan';

/**
 * This class represents the controller for editing a Workflow.
 */
class LayoutViewWorkflowBuilder extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     */
    initialize()
    {
        this._initializeRadio();
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__UPDATER_CLEAR);
        this._lastErrorCode = '';
        this._lastErrorDetails = '';
    }

    /**
     * After render.
     */
    onRender()
    {
        this._handleClickCheckboxAddPorts(); 
    }

    /**
     * Unbind from events.
     */
    onDestroy()
    {
        this.guiChannel.trigger(GUI_EVENTS.EVENT__WORKFLOWBUILDER_GUI_DESTROY);

        this.rodanChannel.off(null, null, this);
        this.rodanChannel.stopReplying(null, null, this);
        this.guiChannel.off(null, null, this);
        this.guiChannel.stopReplying(null, null, this);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        this.rodanChannel = Radio.channel('rodan');
        this.guiChannel = Radio.channel('rodan-client_gui');
        this.rodanChannel.on(Rodan.RODAN_EVENTS.EVENT__SERVER_ERROR, options => this._handleEventRodanError(options), this);
    }

    /**
     * Handle button zoom in.
     */
    _handleButtonZoomIn()
    {
        this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_IN);
    }
    
    /**
     * Handle button zoom out.
     */
    _handleButtonZoomOut()
    {
        this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_OUT);
    }
    
    /**
     * Handle button zoom reset.
     */
    _handleButtonZoomReset()
    {
        this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ZOOM_RESET);
    }
    
    /**
     * Handle button edit.
     */
    _handleButtonEdit()
    {
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOW_VIEW, {workflow: this.model});
    }
    
    /**
     * Handle button add job.
     */
    _handleButtonAddJob()
    {
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_JOBCOLLECTION_VIEW, {workflow: this.model});
    }
    
    /**
     * Handle button import workflow.
     */
    _handleButtonImportWorkflow()
    {
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_WORKFLOWCOLLECTION_VIEW, {workflow: this.model});
    }
    
    /**
     * Handle button run.
     */
    _handleButtonRun()
    {
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_CREATE_WORKFLOWRUN, {workflow: this.model});
    }

    /**
     * Handle event Workflow updated.
     */
    _handleEventRodanError(options)
    {
        this._lastErrorCode = options.json.error_code;
        this._lastErrorDetails = options.json.details[0];
    }

    /**
     * Handle click data status.
     */
    _handleClickDataStatus()
    {
        if (this._lastErrorCode !== '' || this._lastErrorDetails !== '')
        {   
            this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__MODAL_SHOW, {title: "ERROR", content: "Error code: " + this._lastErrorCode + " " + this._lastErrorDetails});
        }
    }

    /**
     * Handle click on checkbox.
     */
    _handleClickCheckboxAddPorts()
    {
        var checked = this.ui.checkboxAddPorts.is(':checked'); 
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SET_ADDPORTS, {addports: checked});
    }

    /**
     * Updates info of Workflow in view.
     */
    _updateView(event, model)
    {
        if (this.model.get('valid'))
        {
            this._lastErrorCode = '';
            this._lastErrorDetails = '';
            this.ui.dataStatus.text('Workflow "' + this.model.get('name') + '" is valid'); 
        }
        else
        {
            if (this._lastErrorCode == '' && this._lastErrorDetails == '') {
                this.ui.dataStatus.text('Workflow "' + this.model.get('name') + '" setup is incomplete.'); 
            } else {
                this.ui.dataStatus.text('Workflow "' + this.model.get('name') + '" is INVALID (click here for details)'); 
            }
        }
    }
}

///////////////////////////////////////////////////////////////////////////////////////
// PROTOTYPE
///////////////////////////////////////////////////////////////////////////////////////
LayoutViewWorkflowBuilder.prototype.template = _.template($('#template-main_workflowbuilder').text());
LayoutViewWorkflowBuilder.prototype.ui = {
    buttonZoomIn: '#button-zoom_in',
    buttonZoomOut: '#button-zoom_out',
    buttonZoomReset: '#button-zoom_reset',
    checkboxAddPorts: '#checkbox-add_ports',
    dataStatus: '#data-workflow_status',
    buttonEdit: '#button-edit',
    buttonAddJob: '#button-add_job',
    buttonImportWorkflow: '#button-import_workflow',
    buttonRun: '#button-run'
};
LayoutViewWorkflowBuilder.prototype.events = {
    'click @ui.buttonZoomIn': '_handleButtonZoomIn',
    'click @ui.buttonZoomOut': '_handleButtonZoomOut',
    'click @ui.buttonZoomReset': '_handleButtonZoomReset',
    'click @ui.dataStatus': '_handleClickDataStatus',
    'change @ui.checkboxAddPorts': '_handleClickCheckboxAddPorts',
    'click @ui.buttonEdit': '_handleButtonEdit',
    'click @ui.buttonAddJob': '_handleButtonAddJob',
    'click @ui.buttonImportWorkflow': '_handleButtonImportWorkflow',
    'click @ui.buttonRun': '_handleButtonRun'
};
LayoutViewWorkflowBuilder.prototype.modelEvents = {
    'all': '_updateView'
};

export default LayoutViewWorkflowBuilder;
