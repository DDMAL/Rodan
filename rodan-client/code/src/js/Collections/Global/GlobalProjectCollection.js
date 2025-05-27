import GlobalCollection from './GlobalCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Project from 'js/Models/Project';

let _instance = null;

/**
 * Global Collection of Project models.
 * This uses a pseudo-singleton model so we can inherit from BaseCollection.
 */
export default class GlobalProjectCollection extends GlobalCollection
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
        this.model = Project;
        this._route = 'projects';
        this._allowPagination = true;
        this._loadCommand = RODAN_EVENTS.REQUEST__GLOBAL_PROJECTS_LOAD;
        this._requestCommand = RODAN_EVENTS.REQUEST__GLOBAL_PROJECT_COLLECTION;
    }
}