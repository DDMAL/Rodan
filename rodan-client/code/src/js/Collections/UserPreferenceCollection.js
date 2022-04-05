import BaseCollection from './BaseCollection';
import UserPreference from 'js/Models/UserPreference';

/**
 * Collection of UserPreference models.
 */
export default class UserPreferenceCollection extends BaseCollection
{
    /**
     * Initializes the instance.
     */
    initialize()
    {
        /** @ignore */
        this.model = UserPreference;
        this._route = 'userpreferences';
    }
}