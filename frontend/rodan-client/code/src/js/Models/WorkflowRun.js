import BaseModel from './BaseModel';

/**
 * WorkflowRun.
 */
export default class WorkflowRun extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     */
    initialize()
    {
        this.set('statusText', this._getStatusText(this.get('status')));
    }

    /**
     * Returns defaults.
     *
     * @return {object} object holding default values
     */
    defaults()
    {
        return {created: null, updated: null};
    }

    /**
     * Override of Backbone.Model.parse. This will populate 'statusText' from the existing status.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        this.set('statusText', this._getStatusText(response.status));
        return response;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Return text based on status.
     */
    _getStatusText(status)
    {
        switch(status)
        {
            case -1:
            {
                return 'Failed';
            }

            case 0:
            {
                return 'Scheduled';
            }

            case 1:
            {
                return 'Processing';
            }

            case 2:
            {
                return 'Waiting for input';
            }

            case 4:
            {
                return 'Finished';
            }

            case 8:
            {
                return 'Expired';
            }

            case 9:
            {
                return 'Cancelled';
            }

            case 11:
            {
                return 'Retrying';
            }

            default:
            {
                return 'Unknown status';
            }
        }
    }
}
WorkflowRun.prototype.routeName = 'workflowruns';