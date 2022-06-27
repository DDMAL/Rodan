import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewPassword from './ViewPassword';

/**
 * User view.
 */
export default class ViewUser extends Marionette.CollectionView
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the view.
     */
    initialize()
    {
        /** @ignore */
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_PREFERENCE_LOADED, (options) => this._handleUserPreferenceLoaded(options));
    }

    /**
     * On render, update user preferences if available.
     */
    onRender()
    {
        this._renderUserPreference();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle save button.
     */
    _handleButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__USER_SAVE,
                                  {fields: {first_name: _.escape(this.ui.textFirstName.val()),
                                            last_name: _.escape(this.ui.textLastName.val()),
                                            email: _.escape(this.ui.textEmail.val())}});
        if (this._userPreference)
        {
            this._userPreference.set({'send_email': $(this.ui.checkboxSendEmail).prop('checked')});
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__USER_PREFERENCE_SAVE, {user_preference: this._userPreference});
        }
    }

    /**
     * Handle change password button.
     */
    _handleButtonChangePassword()
    {
        var view = new ViewPassword();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {title: 'Change Password', content: view});

    }

    /**
     * Handle user preference loaded.
     */
    _handleUserPreferenceLoaded(options)
    {
        this._renderUserPreference();
    }

    /**
     * Render user preference.
     */
    _renderUserPreference()
    {
        this._userPreference = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__USER_PREFERENCE);
        if (this._userPreference)
        {
            $(this.ui.divUserPreference).show();
            $(this.ui.divUserPreferenceLoading).hide();
            $(this.ui.checkboxSendEmail).prop('checked', this._userPreference.get('send_email'));
        }
        else
        {
            $(this.ui.divUserPreference).hide();
            $(this.ui.divUserPreferenceLoading).show();
        }
    }
}
ViewUser.prototype.modelEvents = {
            'all': 'render'
        };
ViewUser.prototype.ui = {
            buttonSave: '#button-save_user',
            buttonPassword: '#button-change_password',
            textFirstName: '#text-user_firstname',
            textLastName: '#text-user_lastname',
            textEmail: '#text-user_email',
            checkboxSendEmail: '#checkbox-send_email',
            divUserPreference: '#div-user_preference',
            divUserPreferenceLoading: '#div-user_preference_loading'
        };
ViewUser.prototype.events = {
            'click @ui.buttonSave': '_handleButtonSave',
            'click @ui.buttonPassword': '_handleButtonChangePassword'
        };
ViewUser.prototype.template = _.template($('#template-main_user_individual').text());
