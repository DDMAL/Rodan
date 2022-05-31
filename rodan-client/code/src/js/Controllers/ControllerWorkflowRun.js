import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import LayoutViewIndividualWorkflowRun from 'js/Views/Master/Main/WorkflowRun/Individual/LayoutViewIndividualWorkflowRun';
import Radio from 'backbone.radio';
import ViewWorkflowRunCollection from 'js/Views/Master/Main/WorkflowRun/Collection/ViewWorkflowRunCollection';
import WorkflowRun from 'js/Models/WorkflowRun';
import WorkflowRunCollection from 'js/Collections/WorkflowRunCollection';

/**
 * Controller for WorkflowRun.
 */
export default class ControllerWorkflowRun extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Initialize
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        // Events.
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_CREATED, options => this._handleEventWorkflowRunStartResponse(options)/*this._handleEventWorkflowRunCreationResponse(options)*/);
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_FAILED_TO_CREATE, options => this._handleEventWorkflowRunFailToStartResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_DELETED, options => this._handleEventWorkflowRunDeleteResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_SAVED, options => this._handleEventWorkflowRunSaveResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_STARTED, options => this._handleEventWorkflowRunStartResponse(options));

        // Requests.
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, options => this._handleEventCollectionSelected(options), this);
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED, options => this._handleEventItemSelected(options), this);
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOWRUN_CREATE, options => this._handleRequestWorkflowRunCreate(options), this);
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOWRUN_DELETE, options => this._handleRequestWorkflowRunDelete(options), this);
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOWRUN_SAVE, options => this._handleRequestWorkflowRunSave(options), this);
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__WORKFLOWRUN_START, options => this._handleRequestWorkflowRunStart(options), this);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event WorkflowRun create response.
     */
    _handleEventWorkflowRunCreationResponse(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWRUN_START, {workflowrun: options.workflowrun});
    }

    /**
     * Handle event WorkflowRun delete response.
     */
    _handleEventWorkflowRunDeleteResponse(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, {project: project});
    }

    /**
     * Handle event WorkflowRun save response.
     */
    _handleEventWorkflowRunSaveResponse(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options)
    {
        // Get required collections.
        var runJobs = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RUNJOBS_LOAD, {data: {workflow_run: options.workflowrun.id}});
        var resources = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCES_LOAD, {data: {result_of_workflow_run: options.workflowrun.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [runJobs, resources]});

        // Create view and show.
        this._viewItem = new LayoutViewIndividualWorkflowRun({runjobs: runJobs, resources: resources, model: options.workflowrun});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: this._viewItem});
    }

    /**
     * Handle collection selection.
     */
    _handleEventCollectionSelected(options)
    {
        var collection = new WorkflowRunCollection();
        collection.fetchSort(false, 'created', {data: {project: options.project.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [collection]});
        var view = new ViewWorkflowRunCollection({collection: collection});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: view});
    }

    /**
     * Handle event WorkflowRun start response.
     */
    _handleEventWorkflowRunStartResponse(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, {project: project});
    }

    /**
     * Handle event WorkflowRun fail to start response.
     */
    _handleEventWorkflowRunFailToStartResponse(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);

        // TODO: move this logic as a utility function
        /*
            Translate Django error message into list display.
            HTML structure:
                <dl>
                  <dt>Resource Assignments</dt>
                  <dd>
                    <div>InputPort X</div>
                    <ul>
                      <li>Error 1</li>
                      <li>Error 2</li>
                    </ul>
                    ...
                  </dd>
                  ...
                </dl>
        */
        function getErrorListDisplay(errorList) {
            var fragment = '<ul>';
            for (var i = 0; i < errorList.length; i += 1) {
                fragment += '<li>' + errorList[i] + '</li>';
            }
            fragment += '</ul>';
            return fragment;
        }

        var html = '<dl>';
        var errors = options.errors;
        for (var fieldName in errors) {
            if (errors.hasOwnProperty(fieldName)) {
                var fieldNameDisplay = (fieldName === 'resource_assignments') ? "Resource Assignment" : fieldName;
                html += '<dt>' + fieldNameDisplay + '</dt>';

                html += '<dd>'
                if (fieldName === 'resource_assignments') {
                    var errorMap = errors[fieldName];
                    for (var inputPortUrl in errorMap) {
                        if (errorMap.hasOwnProperty(inputPortUrl)) {
                            html += '<div>InputPort ' + inputPortUrl + '</div>';
                            html += getErrorListDisplay(errorMap[inputPortUrl]);
                        }
                    }
                } else {
                    html += getErrorListDisplay(errors[fieldName]);
                }
                html += '</dd>'
            }
        }
        html += '</dl>'

        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {
            title: 'Error',
            content: html
        });
    }

    /**
     * Handle request create WorkflowRun.
     */
    _handleRequestWorkflowRunCreate(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Creating Workflow Run', content: 'Please wait...'});
        var name = options.workflow.get('name');
        var description = 'Run of Workflow "' + name + '"\n\n' + this._getResourceAssignmentDescription(options.assignments);
        var workflowRun = new WorkflowRun({workflow: options.workflow.get('url'), 
                                           resource_assignments: options.assignments,
                                           name: name,
                                           description: description});
        workflowRun.save({}, {
            success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_CREATED, {workflowrun: model}),
            error: (model, response) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_FAILED_TO_CREATE, {workflowrun: model, errors: response.responseJSON})
        });
    }

    /**
     * Handle request delete WorkflowRun.
     */
    _handleRequestWorkflowRunDelete(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Deleting Workflow Run', content: 'Please wait...'});
        options.workflowrun.destroy({success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_DELETED, {workflowrun: model})});
    }

    /**
     * Handle request save WorkflowRun.
     */
    _handleRequestWorkflowRunSave(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Saving Workflow Run', content: 'Please wait...'});
        options.workflowrun.save(options.workflowrun.changed,
                                 {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SAVED, {workflowrun: model})});
    }

    /**
     * Handle request start WorkflowRun.
     */
    _handleRequestWorkflowRunStart(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Starting Workflow Run', content: 'Please wait...'});
        options.workflowrun.set({status: 21});
        options.workflowrun.save(options.workflowrun.changed,
                                 {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_STARTED, {workflowrun: model})});
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Given resource assignments, provides descriptive info.
     */
    _getResourceAssignmentDescription(assignments)
    {
        var text = '';
        for (var inputPortUrl in assignments)
        {
            var resourceUrls = assignments[inputPortUrl];
            for (var index in resourceUrls)
            {
                text += '- ' + resourceUrls[index] + '\n';
            }
            text += '\n';
        }
        return text;
    }

    /**
     * Handle sync of WorkflowRun elements.
     */
    _handleSyncWorkflowRun(runJobs, resources)
    {
        runJobs.syncCollection();
        resources.syncCollection();
    }
}