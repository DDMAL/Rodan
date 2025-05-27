import BaseCollection from './BaseCollection';
import InputPort from 'js/Models/InputPort';

/**
 * Collection of InputPort models.
 */
export default class InputPortCollection extends BaseCollection
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
        this.model = InputPort;
        this._route = 'inputports';
    }
}