import BaseCollection from './BaseCollection';
import OutputPort from 'js/Models/OutputPort';

/**
 * Collection of OutputPort models.
 */
export default class OutputPortCollection extends BaseCollection
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
        this.model = OutputPort;
        this._route = 'outputports';
    }
}