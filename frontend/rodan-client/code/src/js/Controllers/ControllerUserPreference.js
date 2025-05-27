import $ from 'jquery';
import BaseController from 'js/Controllers/BaseController';
import Configuration from 'js/Configuration';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import UserPreference from 'js/Models/UserPreference';
import UserPreferenceCollection from 'js/Collections/UserPreferenceCollection';
import BaseModel from '../Models/BaseModel';

/**
 * UserPreference controller.
 */
export default class ControllerUserPreference extends BaseController
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
        this._userPreference = null;
        /** @ignore */
        this._collection = new UserPreferenceCollection();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Event bindings.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGIN_SUCCESS, (options) => this._handleEventAuthenticationSuccess(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_PREFERENCE, (options) => this._handleRequestUserPreference(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_PREFERENCE_SAVE, (options) => this._handleRequestUserPreferenceSave(options));
    }

    /**
     * Handle authentication success.
     */
    _handleEventAuthenticationSuccess(options)
    {
        const url = options.user.get("user_preference");
        if (url) {
            const uuid = BaseModel.parseIdFromUrl(url);
            this._userPreference = new UserPreference({ uuid, url });
            this._userPreference.fetch({ success: () => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_PREFERENCE_LOADED, {user_preference: this._userPreference}) });
        } else {
            this._userPreference = new UserPreference({ user: options.user.get('url') });
            this._userPreference.save({ success: () => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_PREFERENCE_LOADED, {user_preference: this._userPreference}) });
        }
    }

    /**
     * Handle request user preference.
     */
    _handleRequestUserPreference()
    {
        return this._userPreference;
    }

    /**
     * Handle request UserPreference save.
     */
    _handleRequestUserPreferenceSave(options)
    {
        if (!$.isEmptyObject(options.user_preference.changed))
        {
            options.user_preference.save(options.user_preference.changed,
                                         {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_PREFERENCE_SAVED, {user_preference: options.user_preference})});
        }
    }
}