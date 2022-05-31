import GlobalCollection from './GlobalCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Job from 'js/Models/Job';

let _instance = null;

/**
 * Global Collection of Job models.
 * This uses a pseudo-singleton model so we can inherit from BaseCollection.
 */
export default class GlobalJobCollection extends GlobalCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @throws {Error} thrown if called more than once
     */
    initialize()
    {
        if (_instance)
        {
            throw new Error('only one instance of this class may exist');
        }
        _instance = this;
        /** @ignore */
        this.model = Job;
        this._route = 'jobs';
        this._loadCommand = RODAN_EVENTS.REQUEST__GLOBAL_JOBS_LOAD;
        this._requestCommand = RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION;
        this._enumerations = new Map();
        this._enumerations.set('category', {label: 'Category'});
        this._enumerations.set('interactive', {label: 'Interactive', values: [{value: 'True', label: 'True'}, {value: 'False', label: 'False'}]});
    }
}