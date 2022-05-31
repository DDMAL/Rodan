import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import NAV_EVENTS from './Events';
import Radio from 'backbone.radio';
import ViewNavigationNode from './ViewNavigationNode';

/**
 * This class represents a navigation menu node for a WorkflowRun Collection.
 */
export default class ViewNavigationNodeWorkflowRuns extends ViewNavigationNode
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
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, event => this._handleEventWorkflowRunsSelected(event));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Send click events.
     */
    _sendClickEvents()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_SET_ACTIVE, {project: this.model.get('project')});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED_COLLECTION, {project: this.model.get('project')});
    }

    /**
     * Handle highlighting.
     */
    _handleEventWorkflowRunsSelected(event)
    {
        if (event.project === this.model.get('project'))
        {
            Radio.channel('rodan-navigation').trigger(NAV_EVENTS.EVENT__NAVIGATION_SELECTED_NODE, {node: this});
        }
    }
}
ViewNavigationNodeWorkflowRuns.prototype.template = _.template($('#template-navigation_workflowruns').text());
