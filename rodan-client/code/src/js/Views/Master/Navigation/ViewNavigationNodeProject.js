import Backbone from 'backbone';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import NAV_EVENTS from './Events';
import Radio from 'backbone.radio';
import Project from 'js/Models/Project';
import ViewNavigationNodeRunJobs from './ViewNavigationNodeRunJobs';
import ViewNavigationNodeResourceLists from './ViewNavigationNodeResourceLists';
import ViewNavigationNodeResources from './ViewNavigationNodeResources';
import ViewNavigationNodeWorkflowRuns from './ViewNavigationNodeWorkflowRuns';
import ViewNavigationNodeWorkflows from './ViewNavigationNodeWorkflows';
import ViewNavigationNode from './ViewNavigationNode';

/**
 * This class represents a navigation menu node for a project.
 */
export default class ViewNavigationNodeProject extends ViewNavigationNode
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     *
     * @param {object} options Marionette.View options object
     */
    initialize(options)
    {
        super.initialize(options);
        /** @ignore */
        this.collection = new Backbone.Collection();
        var resourcesNodeModel = new Backbone.Model({name: 'Resources', project: this.model});
        var resourceListsNodeModel = new Backbone.Model({name: 'Resource Lists', project: this.model});
        var workflowBuilderNodeModel = new Backbone.Model({name: 'Workflows', project: this.model});
        var workflowRunsNodeModel = new Backbone.Model({name: 'Workflow Runs', project: this.model});
        var runJobsNodeModel = new Backbone.Model({name: 'Run Jobs', project: this.model});
        this.collection.add(resourcesNodeModel);
     //   this.collection.add(resourceListsNodeModel);
        this.collection.add(workflowBuilderNodeModel);
        this.collection.add(workflowRunsNodeModel);
        this.collection.add(runJobsNodeModel);
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_SELECTED, event => this._handleEventProjectSelected(event));
    }

    /**
     * Determine child view based on name.
     *
     * @param {BaseModel} model instance of 'Resource', 'Workflow', 'WorkflowRun', or 'RunJob'
     * @return {ViewNavigationNode} a subclass of ViewNavigationNode; only returns class, not instance; will return ViewNavigationNode if the BaseModel provided is not one of the above
     */
    childView(model)
    {
        switch (model.get('name'))
        {
            case 'Resources':
            {
                return ViewNavigationNodeResources;
            }

            case 'Resource Lists':
            {
                return ViewNavigationNodeResourceLists;
            }

            case 'Workflows':
            {
                return ViewNavigationNodeWorkflows;
            }

            case 'Workflow Runs':
            {
                return ViewNavigationNodeWorkflowRuns;
            }

            case 'Run Jobs':
            {
                return ViewNavigationNodeRunJobs;
            }

            default:
            {
                return ViewNavigationNode;
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Send click events.
     */
    _sendClickEvents()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_SELECTED, {project: this.model});
    }

    /**
     * Handle highlighting.
     */
    _handleEventProjectSelected(event)
    {
        if (event.project === this.model)
        {
            Radio.channel('rodan-navigation').trigger(NAV_EVENTS.EVENT__NAVIGATION_SELECTED_NODE, {node: this});
        }
    }
}
