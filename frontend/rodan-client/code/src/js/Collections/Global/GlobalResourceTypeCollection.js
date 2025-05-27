import GlobalCollection from './GlobalCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import ResourceType from 'js/Models/ResourceType';

let _instance = null;

/**
 * Global Collection of ResourceType models.
 * This uses a pseudo-singleton model so we can inherit from BaseCollection.
 */
export default class GlobalResourceTypeCollection extends GlobalCollection
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
        this.model = ResourceType;
        this._route = 'resourcetypes';
        this._loadCommand = RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPES_LOAD;
        this._requestCommand = RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION;
    }
}