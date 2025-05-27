import Radio from 'backbone.radio';
import BaseCollection from './BaseCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Job from 'js/Models/Job';

/**
 * Collection of Job models.
 */
export default class JobCollection extends BaseCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @todo currently getting GlobalJobCollection enumerations for these enums; need a better way
     */
    initialize()
    {
        var globalJobCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION);
        /** @ignore */
        this.model = Job;
        this._route = 'jobs';
        this._enumerations = globalJobCollection._enumerations;
    }
}