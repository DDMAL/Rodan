import BaseCollection from './BaseCollection';
import OutputPortType from 'js/Models/OutputPortType';

/**
 * Collection of OutputPortType models.
 */
export default class OutputPortTypeCollection extends BaseCollection
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
        this.model = OutputPortType;
        this._route = 'outputporttypes';
    }
}