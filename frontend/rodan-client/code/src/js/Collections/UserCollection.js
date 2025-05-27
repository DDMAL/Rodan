import BaseCollection from './BaseCollection';
import User from 'js/Models/User';

/**
 * Collection of User models.
 */
export default class UserCollection extends BaseCollection
{
    /**
     * Initializes the instance.
     */
    initialize()
    {
        /** @ignore */
        this.model = User;
        this._route = 'users';
    }
}