import BaseCollection from './BaseCollection';
import InputPortType from 'js/Models/InputPortType';

/**
 * Collection of InputPortType models.
 */
export default class InputPortTypeCollection extends BaseCollection
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
        this.model = InputPortType;
        this._route = 'inputporttypes';
    }
}