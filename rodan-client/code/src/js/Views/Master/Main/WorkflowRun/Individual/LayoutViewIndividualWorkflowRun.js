import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import LayoutViewModel from 'js/Views/Master/Main/LayoutViewModel';
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
        this._runJobs = options.runjobs;
        this._resources = options.resources;
        this.addRegions({
            regionRunJobCollection: '#region-main_workflowrun_individual_runjobs',
            regionResourceCollection: '#region-main_workflowrun_individual_resources'
        });
    }

    /**
     * Insert subviews after render.
     */
    onRender()
    {
        // Empty regions.
        this.getRegion('regionRunJobCollection').empty();
        this.getRegion('regionResourceCollection').empty();

        if (this.getRegion('regionRunJobCollection').el === undefined || this.getRegion('regionResourceCollection').el === undefined) {
          this.getRegion('regionRunJobCollection').el = '#region-main_workflowrun_individual_runjobs'
          this.getRegion('regionResourceCollection').el = '#region-main_workflowrun_individual_resources'
        }

        // Create Resource collection view.
        this._layoutViewResources = new LayoutViewModel();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_SHOWLAYOUTVIEW, {layoutView: this._layoutViewResources});
        this.showChildView('regionResourceCollection', this._layoutViewResources);
        this._viewResourceCollection = new ViewResourceCollection({collection: this._resources,
                                                       template: _.template($('#template-main_workflowrun_individual_resources_collection').text()),
                                                       childView: ViewResourceCollectionItem});
        this._layoutViewResources.showCollection(this._viewResourceCollection);

        // Create RunJob collection view.
        this._layoutViewRunJobs = new LayoutViewModel();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RUNJOB_SHOWLAYOUTVIEW, {layoutView: this._layoutViewRunJobs});
        this.showChildView('regionRunJobCollection', this._layoutViewRunJobs);
        this._viewRunJobCollection = new ViewRunJobCollection({collection: this._runJobs,
                                                   template: _.template($('#template-main_runjob_collection_notitle').text()),
                                                   childView: ViewRunJobCollectionItem});
        this._layoutViewRunJobs.showCollection(this._viewRunJobCollection);

        // Show Resources on default.
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
        this.getRegion('regionRunJobCollection').$el.hide();
        this.ui.buttonShowResources.css('text-decoration', 'underline');
        this.ui.buttonShowRunJobs.css('text-decoration', 'none');
        if (!this.getRegion('regionResourceCollection').$el.is(':visible'))
        {
            this.getRegion('regionResourceCollection').$el.toggle('fast');
        }
    }

    /**
     * Handle button show RunJobs.
     */
    _showRunJobs()
    {
        this.getRegion('regionResourceCollection').$el.hide();
        this.ui.buttonShowResources.css('text-decoration', 'none');
        this.ui.buttonShowRunJobs.css('text-decoration', 'underline');
        if (!this.getRegion('regionRunJobCollection').$el.is(':visible'))
        {
            this.getRegion('regionRunJobCollection').$el.toggle('fast');
        }
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
