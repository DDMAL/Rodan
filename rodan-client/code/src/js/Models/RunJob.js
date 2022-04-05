import BaseModel from './BaseModel';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * RunJob.
 */
export default class RunJob extends BaseModel
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
        this.set('available', this.available());
    }

    /**
     * Return true if the current user can lock as a manual RunJob.
     *
     * @return {boolean} true if the current user can lock as a manual RunJob
     */
    available()
    {
        var currentUser = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_USER);
        if (this.get('interactive_acquire') !== null && this.get('status') === 2)
        {
            var serverDate = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_DATE);
            var expiryDate = new Date(this.get('working_user_expiry'));
            if (this.get('working_user') === null ||
                this.get('working_user') === currentUser.get('url') ||
                serverDate.getTime() > expiryDate.getTime())
            {
                return true;
            }
        }
        return false;
    }

    /**
     * Override of Backbone.Model.parse. Sets the 'statusText' field.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        response.statusText = this._getStatusText(response.status);
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
RunJob.prototype.routeName = 'runjobs';