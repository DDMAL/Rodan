import BaseCollection from './BaseCollection';
import Project from 'js/Models/Project';

/**
 * Collection of Project models.
 */
export default class ProjectCollection extends BaseCollection
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
        this.model = Project;
        this._route = 'projects';
    }
}