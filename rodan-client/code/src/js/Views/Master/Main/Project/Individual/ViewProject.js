import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Project view.
 */
export default class ViewProject extends Marionette.CollectionView
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_SAVE,
                                  {project: this.model,
                                   fields: {name: _.escape(this.ui.textName.val()), description: _.escape(this.ui.textDescription.val())}});
    }

    /**
     * Handle delete button.
     */
    _handleButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_DELETE, {project: this.model});
    }

    /**
     * Handle RunJob button.
     */
    _handleButtonRunJobs()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_SELECTED_COLLECTION, {project: this.model});
    }

    /**
     * Handle click resource count.
     */
    _handleClickResourceCount()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_SELECTED_COLLECTION, {project: this.model});
    }

    /**
     * Handle click workflow count.
     */
    _handleClickWorkflowCount()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED_COLLECTION, {project: this.model});
    }

    /**
     * Handle click button ResourceLists.
     */
    _handleButtonResourceLists()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED_COLLECTION, {project: this.model});
    }

    /**
     * Handle button Project users.
     */
    _handleButtonProjectUsers()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this.model});
    }
}
ViewProject.prototype.modelEvents = {
            'all': 'render'
        };
ViewProject.prototype.ui = {
            buttonSave: '#button-save_project',
            buttonDelete: '#button-delete_project',
            buttonResourceLists: '#button-resourcelists',
            resourceCount: '#resource_count',
            workflowCount: '#workflow_count',
            buttonRunJobs: '#button-runjobs',
            textName: '#text-project_name',
            textDescription: '#text-project_description',
            buttonUsers: '#button-project_users'
        };
ViewProject.prototype.events = {
            'click @ui.buttonSave': '_handleButtonSave',
            'click @ui.buttonDelete': '_handleButtonDelete',
            'click @ui.resourceCount': '_handleClickResourceCount',
            'click @ui.workflowCount': '_handleClickWorkflowCount',
            'click @ui.buttonRunJobs': '_handleButtonRunJobs',
            'click @ui.buttonResourceLists': '_handleButtonResourceLists',
            'click @ui.buttonUsers': '_handleButtonProjectUsers'
        };
ViewProject.prototype.template = _.template($('#template-main_project_individual').text());
