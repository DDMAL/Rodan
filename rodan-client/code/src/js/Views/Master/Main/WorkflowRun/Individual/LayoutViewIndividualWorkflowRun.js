import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewResourceCollection from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollection';
import ViewResourceCollectionItem from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollectionItem';
import ViewRunJobCollection from 'js/Views/Master/Main/RunJob/Collection/ViewRunJobCollection';
import ViewRunJobCollectionItem from 'js/Views/Master/Main/RunJob/Collection/ViewRunJobCollectionItem';

/**
 * WorkflowRun view.
 */
export default class LayoutViewIndividualWorkflowRun extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.runjobs' (RunJobCollection) and 'options.resources' (ResourceCollection) must also be provided
     */
    initialize(options)
    {
        // console.log(options);
        this._projectView = options.projectView;
        this._activeProject = options.activeProject;
        this._runJobs = options.runjobs;
        this._resources = options.resources;
        this.addRegions({
            regionRunJobCollection: '#region-main_workflowrun_individual_runjobs',
            regionResourceCollection: '#region-main_workflowrun_individual_resources'
        });
        this.setElement('<div class="content-wrapper row-content"></div>');
    }

    /**
     * Insert subviews after render.
     */
    onRender()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_SHOWLAYOUTVIEW, {projectView: this._projectView});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RUNJOB_SHOWLAYOUTVIEW, {projectView: this._projectView});

        // Create Resource collection view.
        this._viewResourceCollection = new ViewResourceCollection({
            collection: this._resources,
            template: _.template($('#template-main_workflowrun_individual_resources_collection').text()),
            childView: ViewResourceCollectionItem
        });     

        // Create RunJob collection view.
        this._viewRunJobCollection = new ViewRunJobCollection({
            collection: this._runJobs,
            template: _.template($('#template-main_runjob_collection_notitle').text()),
            childView: ViewRunJobCollectionItem
        });

        // Show Resource collection view by default.
        // If needed, this can be changed to show RunJob collection view by default (_showRunJobs()).
        // Consult with regular Rodan users and researchers before changing.
        this._showResources();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button show Resources.
     */
    _showResources()
    {
        this.detachChildView('regionRunJobCollection');
        this.showChildView('regionResourceCollection', this._viewResourceCollection)
        this.ui.buttonShowResources.addClass('active');
        this.ui.buttonShowRunJobs.removeClass('active');
    }

    /**
     * Handle button show RunJobs.
     */
    _showRunJobs()
    {
        // Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_SELECTED, {project: this._activeProject});
        this.detachChildView('regionResourceCollection')
        this.showChildView('regionRunJobCollection', this._viewRunJobCollection)
        this.ui.buttonShowRunJobs.addClass('active');
        this.ui.buttonShowResources.removeClass('active');        
    }

    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        this.model.set({name: _.escape(this.ui.textName.val()), description: _.escape(this.ui.textDescription.val())});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWRUN_SAVE, {workflowrun: this.model});
    }

    /**
     * Handle button delete.
     */
    _handleButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWRUN_DELETE, {workflowrun: this.model});
    }
}
LayoutViewIndividualWorkflowRun.prototype.modelEvents = {
    'all': 'render'
};
LayoutViewIndividualWorkflowRun.prototype.ui = {
    buttonShowResources: '#button-resources_show',
    buttonShowRunJobs: '#button-runjobs_show',
    buttonSave: '#button-save_workflowrun',
    buttonDelete: '#button-delete_workflowrun',
    textName: '#text-workflowrun_name',
    textDescription: '#text-workflowrun_description'
};
LayoutViewIndividualWorkflowRun.prototype.events = {
    'click @ui.buttonShowResources': '_showResources',
    'click @ui.buttonShowRunJobs': '_showRunJobs',
    'click @ui.buttonSave': '_handleButtonSave',
    'click @ui.buttonDelete': '_handleButtonDelete'

};
LayoutViewIndividualWorkflowRun.prototype.template = _.template($('#template-main_workflowrun_individual').text());
