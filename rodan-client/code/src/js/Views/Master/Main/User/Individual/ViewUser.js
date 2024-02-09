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
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MODAL_FORM_VALIDATION_ERROR, (options) => this._handleErrors(options));
        this.setElement('<div class="content-wrapper column-content"></div>');
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
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__USER_SAVE, {
            fields: {
                username: _.escape(this.ui.textUsername.val()),
                first_name: _.escape(this.ui.textFirstName.val()),
                last_name: _.escape(this.ui.textLastName.val()),
                email: _.escape(this.ui.textEmail.val())
            }
        });
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

    /**
     * Handle errors.
     */
    _handleErrors(options)
    {
        for (const [key, errors] of Object.entries(options.errors)) {
            switch (key) {
                case 'username':
                    $(this.ui.errorUsername).text(errors[0]);
                    break;
                case 'first_name':
                    $(this.ui.errorFirstName).text(errors[0]);
                    break;
                case 'last_name':
                    $(this.ui.errorLastName).text(errors[0]);
                    break;
                case 'email':
                    $(this.ui.errorEmail).text(errors[0]);
                    break;
                default:
                    break;
            }
        }
    }
}
ViewUser.prototype.modelEvents = {
            'all': 'render'
        };
ViewUser.prototype.ui = {
            buttonSave: '#button-save_user',
            buttonPassword: '#button-change_password',
            textUsername: '#text-user_username',
            textFirstName: '#text-user_firstname',
            textLastName: '#text-user_lastname',
            textEmail: '#text-user_email',
            errorUsername: '#error-user_username',
            errorFirstName: '#error-user_firstname',
            errorLastName: '#error-user_lastname',
            errorEmail: '#error-user_email',
            checkboxSendEmail: '#checkbox-send_email',
            divUserPreference: '#div-user_preference',
            divUserPreferenceLoading: '#div-user_preference_loading'
        };
ViewUser.prototype.events = {
            'click @ui.buttonSave': '_handleButtonSave',
            'click @ui.buttonPassword': '_handleButtonChangePassword'
        };
ViewUser.prototype.template = _.template($('#template-main_user_individual').text());
