import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import LayoutViewModel from 'js/Views/Master/Main/LayoutViewModel';
import Radio from 'backbone.radio';
import ViewWorkflow from 'js/Views/Master/Main/Workflow/Individual/ViewWorkflow';
import ViewWorkflowCollection from 'js/Views/Master/Main/Workflow/Collection/ViewWorkflowCollection';
import Workflow from 'js/Models/Workflow';
import WorkflowCollection from 'js/Collections/WorkflowCollection';

/**
 * Controller for Workflows.
 */
export default class ControllerWorkflow extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Initialization
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        // Events.
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED_COLLECTION, options => this._handleEventCollectionSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED, options => this._handleEventItemSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOW_CREATED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOW_DELETED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOW_SAVED, options => this._handleSuccessGeneric(options));

        // Requests.
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOW_SAVE, options => this._handleRequestSaveWorkflow(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOW_DELETE, options => this._handleCommandDeleteWorkflow(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOW_IMPORT, options => this._handleCommandImportWorkflow(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOW_CREATE, options => this._handleCommandAddWorkflow(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOW_EXPORT, options => this._handleCommandExportWorkflow(options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle collection selection.
     */
    _handleEventCollectionSelected(options)
    {
        this._collection = new WorkflowCollection();
        this._collection.fetch({data: {project: options.project.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [this._collection]});
        this._layoutView = new LayoutViewModel();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: this._layoutView});
        this._viewCollection = new ViewWorkflowCollection({collection: this._collection});
        this._layoutView.showCollection(this._viewCollection);
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options)
    {
        this._viewItem = new ViewWorkflow({model: options.workflow});
        this._layoutView.showItem(this._viewItem);
    }

    /**
     * Handle command delete workflow.
     */
    _handleCommandDeleteWorkflow(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Deleting Workflow', content: 'Please wait...'});
        // Clear the individual view (if there).
        if (this._viewItem !== null && options.workflow === this._viewItem.model)
        {
            this._layoutView.clearItemView();
        }
        options.workflow.destroy({success: (model) => this._handleDeleteSuccess(model, this._collection)});
    }

    /**
     * Handle command add workflow.
     */
    _handleCommandAddWorkflow(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Creating Workflow', content: 'Please wait...'});
        var workflow = new Workflow({project: options.project.get('url'), name: 'untitled'});
        workflow.save({}, {success: (model) => this._handleCreateSuccess(model, this._collection)});
    }

    /**
     * Handle save workflow.
     */
    _handleRequestSaveWorkflow(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Saving Workflow', content: 'Please wait...'});
        options.workflow.save(options.fields, {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SAVED, {workflow: model})});
    }

    /**
     * Handle export workflow.
     */
    _handleCommandExportWorkflow(options)
    {
        options.workflow.sync('read', options.workflow, {data: {export: true}, success: (result) => this._handleExportSuccess(result, options.workflow)});
    }

    /**
     * Handle import workflow.
     */
    _handleCommandImportWorkflow(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Importing Workflow', content: 'Please wait...'});
        var fileReader = new FileReader();
        fileReader.onerror = (event) => this._handleFileReaderError(event);
        fileReader.onload = (event) => this._handleFileReaderLoaded(event, options.project);
        fileReader.readAsText(options.file);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - FileReader handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle FileReader error.
     */
    _handleFileReaderError(event)
    {
        // TODO error
        console.error(event);
    }

    /**
     * Handle FileReader loaded.
     */
    _handleFileReaderLoaded(event, project)
    {
        var workflow = new Workflow({project: project.get('url'), serialized: JSON.parse(event.target.result)});
        workflow.save({}, {success: (model) => this._handleImportSuccess(model, this._collection)});
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - REST handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle create success.
     */
    _handleCreateSuccess(model, collection)
    {
        collection.add(model);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_CREATED, {workflow: model});
    }

    /**
     * Handle delete success.
     */
    _handleDeleteSuccess(model, collection)
    {
        collection.remove(model);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_DELETED, {workflow: model});
    }

    /**
     * Handle export success.
     */
    _handleExportSuccess(result, model)
    {
        var data = JSON.stringify(result);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__DOWNLOAD_START, {data: data, filename: model.get('name'), mimetype: 'application/json'});
    }

    /**
     * Handle import success.
     */
    _handleImportSuccess(model, collection)
    {
        collection.add(model, {});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_CREATED, {workflow: model});
        //Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_VALIDATE_WORKFLOW, {workflow: model});
    }

    /**
     * Handle generic success.
     */
    _handleSuccessGeneric(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }
}