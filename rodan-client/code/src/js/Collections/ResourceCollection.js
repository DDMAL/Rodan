import BaseCollection from './BaseCollection';
import Resource from 'js/Models/Resource';

/**
 * Collection of Resource models.
 */
export default class ResourceCollection extends BaseCollection
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
        this.model = Resource;
        this._route = 'resources';
        this._enumerations = new Map();
        this._enumerations.set('uploaded', {label: 'Uploaded or generated', values: [{value: 'False', label: 'Generated'}, {value: 'True', label: 'Uploaded'}]});
    }
}