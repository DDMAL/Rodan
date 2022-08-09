import BaseCollection from './BaseCollection';
import RunJob from 'js/Models/RunJob';

/**
 * Collection of RunJob models.
 */
export default class RunJobCollection extends BaseCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance. This will create custom enumerations for known RunJob states.
     */
    initialize()
    {
        /** @ignore */
        this.model = RunJob;
        this._route = 'runjobs';
        this._enumerations = new Map();
        this._enumerations.set('status', {label: 'Status', values: [{value: -1, label: 'Failed'},
                                                                    {value: 0, label: 'Scheduled'},
                                                                    {value: 1, label: 'Processing'},
                                                                    {value: 2, label: 'Waiting for input'},
                                                                    {value: 4, label: 'Finished'},
                                                                    {value: 8, label: 'Expired'},
                                                                    {value: 9, label: 'Cancelled'},
                                                                    {value: 11, label: 'Retrying'}]});
    }
}