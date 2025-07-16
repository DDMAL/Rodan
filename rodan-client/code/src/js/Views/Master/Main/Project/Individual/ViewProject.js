import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewResourceCollection from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollection';
import ViewWorkflowCollection from 'js/Views/Master/Main/Workflow/Collection/ViewWorkflowCollection';
import ViewWorkflowRunCollection from 'js/Views/Master/Main/WorkflowRun/Collection/ViewWorkflowRunCollection';
import ViewRunJobCollection from 'js/Views/Master/Main/RunJob/Collection/ViewRunJobCollection';

/**
 * Project view.
 */
export default class ViewProject extends Marionette.View {
    /**
     * Initializes the instance.
     */
    initialize() {
        this.setElement('<div id="region-main-content-wrapper" class="content-wrapper column-content"></div>');
        this.addRegions({
            regionCollection: '#region-collection-container',
            // regionProjectInfo: '#region-project-details-panel',
            regionCollectionItemInfo: '#region-collection-item-details-panel'
        });
    }

    /**
     * Show a Collection view.
     *
     * @param {Marionette.View} view Collection view to show
     */
    showCollection(view) {
        this.showChildView('regionCollection', view);

        // Update tab status based on view type
        $('.project-nav-bar-btn').removeClass('active');
        if (view instanceof ViewResourceCollection) {
            $('#resource_count').addClass('active');
        } else if (view instanceof ViewWorkflowCollection) {
            $('#workflow_count').addClass('active');
        } else if (view instanceof ViewWorkflowRunCollection) {
            $('#button-workflow_runs').addClass('active');
        } else if (view instanceof ViewRunJobCollection) {
            $('#button-runjobs').addClass('active');
        }
    }

    /**
     * Show an item view.
     *
     * @param {Marionette.View} view item view to show
     */
    // showProjectInfo(view)
    // {
    //     this.showChildView('regionProjectInfo', view);
    // }

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
    clearCollectionItemInfoView() {
        this.getRegion('regionCollectionItemInfo').empty();
    }
    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSave() {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_SAVE, {
            project: this.model,
            fields: {
                name: _.escape(this.ui.textName.val()),
                description: _.escape(this.ui.textDescription.val())
            }
        });
    }

    /**
     * Handle delete button.
     */
    _handleButtonDelete() {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_DELETE_CONFIRM, { project: this.model });
    }

    /**
     * Handle RunJob button.
     */
    _handleButtonRunJobs() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_SELECTED_COLLECTION, { project: this.model });
    }

    /**
     * Handle click resource count.
     */
    _handleClickResourceCount() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_SELECTED_COLLECTION, { project: this.model });
    }

    /**
     * Handle click workflow count.
     */
    _handleClickWorkflowCount() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED_COLLECTION, { view: this, project: this.model });
    }

    /**
     * Handle button WorkflowRuns.
     */
    _handleButtonWorkflowRuns() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, { project: this.model });
    }

    /**
     * Handle click button ResourceLists.
     */
    _handleButtonResourceLists() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED_COLLECTION, { project: this.model });
        $('.project-nav-bar-btn').removeClass('active');
        $('#resource_count').addClass('active');
    }

    /**
     * Handle button Project users.
     */
    _handleButtonProjectUsers() {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, { project: this.model });
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
    buttonWorkflowRuns: '#button-workflow_runs',
    buttonDeleteProject: '#button-delete_project',
    buttonSaveProject: '#button-save_project',
    textName: '#text-project_name',
    textDescription: '#text-project_description'
};

ViewProject.prototype.events = {
    'click @ui.resourceCount': '_handleClickResourceCount',
    'click @ui.workflowCount': '_handleClickWorkflowCount',
    'click @ui.buttonRunJobs': '_handleButtonRunJobs',
    'click @ui.buttonResourceLists': '_handleButtonResourceLists',
    'click @ui.buttonUsers': '_handleButtonProjectUsers',
    'click @ui.buttonWorkflowRuns': '_handleButtonWorkflowRuns',
    'click @ui.buttonDeleteProject': '_handleButtonDelete',
    'click @ui.buttonSaveProject': '_handleButtonSave'
};

// ViewProject.prototype.template = _.template($('#template-main_layoutview_model').text());
ViewProject.prototype.template = _.template($('#template-main_project_individual').text());
