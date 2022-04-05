import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * WorkflowJobGroup view.
 */
export default class ViewWorkflowJobGroup extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflow' (Workflow) and 'options.workflowjobgroup' (WorkflowJobGroup) must also be provided
     */
    initialize(options)
    {
        this._workflow = options.workflow;
        /** @ignore */
        this.model = options.workflowjobgroup;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button delete.
     */
    _handleButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWJOBGROUP_DELETE, {workflowjobgroup: this.model, workflow: this._workflow});
    }

    /**
     * Handle button ungroup.
     *
     * @todo this shouldn't be calling the workflowbuilder
     */
    _handleButtonUngroup()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_UNGROUP_WORKFLOWJOBGROUP, {workflowjobgroup: this.model, workflow: this._workflow});
    }

    /**
     * Handle button save.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        this.model.set({name: this.ui.textName.val()});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWJOBGROUP_SAVE, {workflowjobgroup: this.model});
    }
}
ViewWorkflowJobGroup.prototype.template = _.template($('#template-main_workflowjobgroup').text());
ViewWorkflowJobGroup.prototype.ui = {
    buttonSave: '#button-save_workflowjobgroup_data',
    buttonDelete: '#button-delete_workflowjobgroup',
    buttonUngroup: '#button-ungroup_workflowjobgroup',
    textName: '#text-workflowjobgroup_name'
};
ViewWorkflowJobGroup.prototype.events = {
    'click @ui.buttonSave': '_handleButtonSave',
    'click @ui.buttonDelete': '_handleButtonDelete',
    'click @ui.buttonUngroup': '_handleButtonUngroup'
};
