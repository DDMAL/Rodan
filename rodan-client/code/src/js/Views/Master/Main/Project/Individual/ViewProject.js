import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Project view.
 */
export default class ViewProject extends Marionette.View
{

    /**
     * Initializes the instance.
     */
    initialize()
    {
        this.setElement('<div id="region-main-content-wrapper" class="content-wrapper column-content"></div>');
        this.addRegions({
            regionCollection: '#region-collection-container',
            regionProjectInfo: '#region-project-info-container',
            regionCollectionItemInfo: '#region-collection-item-info-container'
        });
    }

    /**
     * Show a Collection view.
     *
     * @param {Marionette.View} view Collection view to show
     */
    showCollection(view)
    {
        this.showChildView('regionCollection', view);
    }

    /**
    * Show an item view.
    *
    * @param {Marionette.View} view item view to show
    */
    showProjectInfo(view)
    {
        this.showChildView('regionProjectInfo', view);
    }

    /**
    * Show an item view. This is for the secondary item view.
    * 
    * @param {Marionette.View} view item view to show
    */
    showCollectionItemInfo(view) {
        this.showChildView('regionCollectionItemInfo', view);
    }

    /**
    * Clears item view.
    */
    clearCollectionItemInfoView()
    {
        this.getRegion('regionCollectionItemInfo').empty();
    }
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_SAVE, 
                                        {
                                            project: this.model,
                                            fields: {
                                                name: _.escape(this.ui.textName.val()), 
                                                description: _.escape(this.ui.textDescription.val())
                                            }
                                        }
        );
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
        $('.project-nav-bar-btn').removeClass('active');
        $('#button-runjobs').addClass('active');
    }

    /**
    * Handle click resource count.
    */
    _handleClickResourceCount()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_SELECTED_COLLECTION, {project: this.model});
        $('.project-nav-bar-btn').removeClass('active');
        $('#resource_count').addClass('active');
    }

    /**
    * Handle click workflow count.
    */
    _handleClickWorkflowCount()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED_COLLECTION, {view: this, project: this.model});
        $('.project-nav-bar-btn').removeClass('active');
        $('#workflow_count').addClass('active');
    }

    _handleButtonWorkflowRuns()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, {project: this.model});
        $('.project-nav-bar-btn').removeClass('active');
        $('#button-workflow_runs').addClass('active');
    }

    /**
    * Handle click button ResourceLists.
    */
    _handleButtonResourceLists()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED_COLLECTION, {project: this.model});
        $('.project-nav-bar-btn').removeClass('active');
        $('#resource_count').addClass('active');
    }

    /**
    * Handle button Project users.
    */
    _handleButtonProjectUsers()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this.model});
        $('.project-nav-bar-btn').removeClass('active');
        $('#button-project_users').addClass('active');
    }
}
ViewProject.prototype.ui = {
    // buttonResourceLists: '#button-resourcelists',
    resourceCount: '#resource_count',
    workflowCount: '#workflow_count',
    buttonRunJobs: '#button-runjobs',
    buttonUsers: '#button-project_users',
    buttonWorkflowRuns: '#button-workflow_runs'
};

ViewProject.prototype.events = {
    'click @ui.resourceCount': '_handleClickResourceCount',
    'click @ui.workflowCount': '_handleClickWorkflowCount',
    'click @ui.buttonRunJobs': '_handleButtonRunJobs',
    'click @ui.buttonResourceLists': '_handleButtonResourceLists',
    'click @ui.buttonUsers': '_handleButtonProjectUsers',
    'click @ui.buttonWorkflowRuns': '_handleButtonWorkflowRuns'
};

// ViewProject.prototype.template = _.template($('#template-main_layoutview_model').text());
ViewProject.prototype.template = _.template($('#template-main_project_individual').text());
