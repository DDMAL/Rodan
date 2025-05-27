import BaseCollection from './BaseCollection';
import Workflow from 'js/Models/Workflow';

/**
 * Collection of Workflow models.
 */
export default class WorkflowCollection extends BaseCollection
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
        this.model = Workflow;
        this._route = 'workflows';
    }
}