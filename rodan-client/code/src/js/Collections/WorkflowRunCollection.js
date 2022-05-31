import BaseCollection from './BaseCollection';
import WorkflowRun from 'js/Models/WorkflowRun';

/**
 * Collection of WorkflowRun models.
 */
export default class WorkflowRunCollection extends BaseCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        /** @ignore */
        this.model = WorkflowRun;
        this._route = 'workflowruns';
    }
}