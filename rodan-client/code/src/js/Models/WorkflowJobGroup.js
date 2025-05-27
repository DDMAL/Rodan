import BaseModel from './BaseModel';

/**
 * WorkflowJobGroup.
 */
export default class WorkflowJobGroup extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns defaults.
     *
     * @return {object} object holding default values
     */
    defaults()
    {
        return {name: 'untitled'};
    }
}
WorkflowJobGroup.prototype.routeName = 'workflowjobgroups';