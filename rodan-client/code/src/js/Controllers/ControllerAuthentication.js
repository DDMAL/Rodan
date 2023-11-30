import BaseController from 'js/Controllers/BaseController';
import Configuration from 'js/Configuration';
import Cookie from 'js/Shared/Cookie';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import User from 'js/Models/User';
import ViewActivationRequired from '../Views/Master/Main/Login/ViewActivationRequired';

/**
 * Controls authentication.
 */
export default class ControllerAuthentication extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * How authentication behaves depends on Configuration.SERVER_AUTHENTICATION_TYPE.
     */
    initialize()
    {
        this._user = null;
        if (Configuration.SERVER_AUTHENTICATION_TYPE === 'session')
        {
            this._token = new Cookie('csrftoken');
        }
        else if (Configuration.SERVER_AUTHENTICATION_TYPE === 'token')
        {
            this._token = new Cookie('token');
        }
        else
        {
            /** @todo throw error if bad authentication type. */
        }
    }

    /**
     * AJAX prefilter associated with authentication.
     *
     * This will make sure that the appropriate request headers for authentication are set on all AJAX requests to the server.
     *
     * @param {object} options object.beforeSend (optional) is a function that takes in the XmlHTTPRequest before sending; this may be useful for doing pre-processing of AJAX requests
     */
    ajaxPrefilter(options)
    {
        var that = this;
        var oldOnBeforeSend = options.beforeSend;
        if (Configuration.SERVER_AUTHENTICATION_TYPE === 'session' && !options.beforeSend) 
        {
            options.xhrFields = { withCredentials: true };
            options.beforeSend = function (xhr) 
            {
                if (oldOnBeforeSend)
                {
                    oldOnBeforeSend(xhr);
                }
                if (that._token.value)
                {
                    xhr.setRequestHeader('X-CSRFToken', that._token.value);
                }
                
            };
        }
        else if(Configuration.SERVER_AUTHENTICATION_TYPE === 'token')
        {
            options.beforeSend = function (xhr)
            {
                if (oldOnBeforeSend)
                {
                    oldOnBeforeSend(xhr);
                }
                if (that._token.value)
                {
                    xhr.setRequestHeader('Authorization', 'Token ' + that._token.value);
                }
            };
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_SAVED, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_CHANGED_PASSWORD, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_PASSWORD_RESET_REQUESTED, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_PASSWORD_RESET_CONFIRMED, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_REGISTERED, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_ACTIVATED, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__USER_RESENT_ACTIVATION_EMAIL, (options) => this._handleEventGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__AUTHENTICATION_ACTIVATION_REQUIRED, (options) => this._handleActivationRequired(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_CHANGE_PASSWORD, (options) => this._handleRequestChangePassword(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_RESET_PASSWORD, (options) => this._handleRequestResetPassword(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_RESET_PASSWORD_CONFIRM, (options) => this._handleRequestResetPasswordConfirm(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_SAVE, (options) => this._handleRequestSaveUser(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_REGISTER, (options) => this._handleRequestRegister(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_ACTIVATE_ACCOUNT, (options) => this._handleRequestActivateAccount(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__USER_RESEND_ACTIVATION, (options) => this._handleResendActivationEmail(options));

        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__AUTHENTICATION_USER, () => this._handleRequestUser());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__AUTHENTICATION_LOGIN, options => this._login(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__AUTHENTICATION_CHECK, () => this._checkAuthenticationStatus());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__AUTHENTICATION_LOGOUT, () => this._logout());
    }

    /**
     * Handle authentication response.
     */
    _handleAuthenticationResponse(event, email)
    {
        var request = event.currentTarget;
        if (request.responseText === null)
        {
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_ERROR_NULL);
        }
        
        switch (request.status)
        {
            case 200:
                var parsed = JSON.parse(request.responseText);
                this._user = new User(parsed);
                this._processAuthenticationData();
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGIN_SUCCESS, {user: this._user});
                break;
            case 400:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGINREQUIRED);
                break;
            case 401:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request,
                                                                           message: 'Incorrect email/password.'});
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGINREQUIRED);
                break;
            case 403:
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_ACTIVATION_REQUIRED, {email});
                break;
            default:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                break;
        }
    }

    /**
     * Handle deauthentication response.
     */
    _handleDeauthenticationResponse(event)
    {
        var request = event.currentTarget;
        if (request.responseText === null)
        {
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_ERROR_NULL);
        }

        switch (request.status)
        {
            case 200:
            case 204:
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGOUT_SUCCESS);
                break;
            case 400:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                break;
            case 401:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                break;
            case 403:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                break;
            default:
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: request});
                break;
        }
    }

    /**
     * Handle timeout.
     */
    _handleTimeout(event)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_WENTAWAY, {event: event});
    }

    /**
     * Sends request to check authentication.
     */
    _checkAuthenticationStatus()
    {
        // First, check if we have the appropriate authentication data. If we do, check it.
        // If we don't, trigger an event to inform of login require.
        if (this._token.value === '')
        {
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGINREQUIRED);
        }
        else
        {
            var authRoute = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-me');
            var request = new XMLHttpRequest();
            request.onload = (event) => this._handleAuthenticationResponse(event);
            request.ontimeout = (event) => this._handleTimeout(event);
            request.open('GET', authRoute, true);
            request.setRequestHeader('Accept', 'application/json');
            this._setAuthenticationData(request);
            request.send();
        }
    }

    /**
     * Login.
     */
    _login(options)
    {
        var authRoute = this._getAuthenticationRoute();
        var authType = Configuration.SERVER_AUTHENTICATION_TYPE;
        var request = new XMLHttpRequest();
        request.onload = (event) => this._handleAuthenticationResponse(event, options.email);
        request.ontimeout = (event) => this._handleTimeout(event);
        request.open('POST', authRoute, true);
        if (authType === 'session')
        {
            request.withCredentials = true;
        }
        request.setRequestHeader('Accept', 'application/json');
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        request.send('email=' + options.email + '&password=' + options.password);
    }

    /**
     * Logout.
     */
    _logout()
    {
        var authRoute = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-reset-token');
        var request = new XMLHttpRequest();
        request.onload = (event) => this._handleDeauthenticationResponse(event);
        request.ontimeout = (event) => this._handleTimeout(event);
        request.open('POST', authRoute, true);
        request.setRequestHeader('Accept', 'application/json');
        this._setAuthenticationData(request);
        this._deleteAuthenticationData();
        request.send();
        this._user = null;
    }

    /**
     * Sets the appropriate authentication data to the request.
     */
    _setAuthenticationData(request)
    {
        if (Configuration.SERVER_AUTHENTICATION_TYPE === 'token' && this._token.value)
        {
            request.setRequestHeader('Authorization', 'Token ' + this._token.value);
        }
        else if (Configuration.SERVER_AUTHENTICATION_TYPE === 'session' && this._token.value)
        {
            request.withCredentials = true;
            request.setRequestHeader('X-CSRFToken', this._token.value);
        }   
    }

    /**
     * Deletes authentication data.
     */
    _deleteAuthenticationData()
    {
        // Only need to worry about token authentication.
        if (Configuration.SERVER_AUTHENTICATION_TYPE === 'token')
        {
            Cookie.saveCookie('token', '', 0);
            this._token = new Cookie('token');
        }
    }

    /** 
     * Save authentication data.
     */
    _processAuthenticationData()
    {
        if (Configuration.SERVER_AUTHENTICATION_TYPE === 'token' && this._user.has('token'))
        {
            Cookie.saveCookie('token', this._user.get('token'), 365);
            this._token = new Cookie('token');
        }
        else if (Configuration.SERVER_AUTHENTICATION_TYPE === 'session')
        {
            this._token = new Cookie('csrftoken');
        }
    }

    /**
     * Send out active user.
     */
    _handleRequestUser()
    {
        return this._user;
    }

    /**
     * Returns authentication route.
     */
    _getAuthenticationRoute()
    {
        switch (Configuration.SERVER_AUTHENTICATION_TYPE)
        {
            case 'session':
            {
                return Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'session-auth');
            }

            case 'token':
            {
                return Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-token');
            }

            default:
            {
                console.error('An acceptable Authentication Type was not provided');
                break;
            }
        }
    }

    /**
     * Handle event generic.
     */
    _handleEventGeneric()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }

    /**
     * Handle request save User.
     */
    _handleRequestSaveUser(options)
    {
        var route = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-me');
        var ajaxSettings = {success: (response) => this._handleSaveUserSuccess(response),
                            error: (response) => this._handleSaveUserError(response),
                            type: 'PATCH',
                            url: route,
                            dataType: 'json',
                            data: options.fields};
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Saving User', content: 'Please wait...'});
    }

    /**
     * Handle request change password.
     */
    _handleRequestChangePassword(options)
    {
        var route = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-change-password');
        var ajaxSettings = {success: (response) => this._handleChangePasswordSuccess(response),
                        //    error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                            type: 'POST',
                            url: route,
                         //   dataType: 'json',
                            data: {new_password: options.newpassword, current_password: options.currentpassword}};
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Saving password', content: 'Please wait...'});
    }

    _handleRequestResetPassword(options)
    {
        const route = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-reset-password');
        const ajaxSettings = {
            success: (response) => this._handleRequestPasswordResetSuccess(response),
            type: 'POST',
            url: route,
            data: { email: options.email }
        };
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, { settings: ajaxSettings });
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Requesting password reset', content: 'Please wait...'});
    }

    /**
     * Handles password reset confirmation.
     */
    _handleRequestResetPasswordConfirm(options)
    {
        const route = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-reset-password-confirm');
        const ajaxSettings = {
            success: (response) => this._handleResetPasswordConfirmationSuccess(response),
            error: (response) => this._handleResetPasswordConfirmationError(response),
            type: 'POST',
            url: route,
            data: { uid: options.uid, token: options.token, new_password: options.new_password }
        };
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, { settings: ajaxSettings });
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Resetting password', content: 'Please wait...'});
    }

    /**
     * Handle response from saving user.
     */
    _handleSaveUserSuccess(response)
    {
        this._user = new User(response);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_SAVED, {user: this._user});
    }

    /**
     * Handles errors from saving user.
     */
    _handleSaveUserError(response)
    {
        const errors = response.responseJSON;
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_FORM_VALIDATION_ERROR, { errors });
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, {content: 'An error occured while saving the user.'});
    }

    /**
     * Handle success response from changing password.
     */
    _handleChangePasswordSuccess(response)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_CHANGED_PASSWORD);
    }

    /**
     * Handle reset password request success
     */
    _handleRequestPasswordResetSuccess(response)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_PASSWORD_RESET_REQUESTED);
    }

    /**
     * Handle reset password confirm success.
     */
    _handleResetPasswordConfirmationSuccess(response)
    {
        Backbone.history.navigate('');
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__USER_PASSWORD_RESET_CONFIRMED);
    }

    /**
     * Handle error response from reset password attempt.
     */
    _handleResetPasswordConfirmationError(response)
    {
        const errors = Object.values(response.responseJSON);
        const content = errors.flat().join(" ");
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, { content });
    }

    /**
     * Handles registration request.
     */
    _handleRequestRegister(options)
    {
        const route = Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'auth-register');
        const ajaxSettings = {
            success: (response) => this._handleRequestRegisterSuccess(response),
            error: (response) => this._handleRequestRegisterError(response),
            type: "POST",
            url: route,
            data: { first_name: options.firstName, last_name: options.lastName, username: options.username, email: options.email, password: options.password }
        };
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, { settings: ajaxSettings });
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Registering', content: 'Please wait...'});
    }

    /**
     * Handle success response from register attempt.
     */
    _handleRequestRegisterSuccess(response)
    {
        Radio.channel("rodan").trigger(RODAN_EVENTS.EVENT__USER_REGISTERED);
    }

    /**
     * Handle error response from register attempt.
     */
    _handleRequestRegisterError(response)
    {
        const errors = response.responseJSON;
        Radio.channel("rodan").trigger(RODAN_EVENTS.EVENT__USER_REGISTER_ERROR, { errors });
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_ERROR, { content: "An error occured during registration." });
    }

    /**
     * Handles request to activate account.
     */
    _handleRequestActivateAccount(options)
    {
        const { uid, token } = options;
        const route = Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, "auth-activate");
        const ajaxSettings = {
            success: (response) => this._handleRequestActivateAccountSuccess(response),
            error: (response) => this._handleRequestActivateAccountError(response),
            type: "POST",
            url: route,
            data: { uid, token }
        };
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, { settings: ajaxSettings });
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: "Activate Account", content: "Activating your account..." });
    }

    /**
     * Handle success response from activate account.
     */
    _handleRequestActivateAccountSuccess(response)
    {
        Backbone.history.navigate("");
        Radio.channel("rodan").trigger(RODAN_EVENTS.EVENT__USER_ACTIVATED);
    }

    /**
     * Handles error response from activate account.
     */
    _handleRequestActivateAccountError(response)
    {
        const error = response.responseJSON.detail;
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_ERROR, { content: error });
    }

    /**
     * Shows activation required modal.
     */
    _handleActivationRequired(options)
    {
        const view = new ViewActivationRequired(options);
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_SHOW, { title: "Activation Required", content: view });
    }

    /**
     * Requests new activation email.
     */
    _handleResendActivationEmail(options)
    {
        const route = Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, "auth-resend-activation");
        const ajaxSettings = {
            success: (response) => this._handleResendActivationEmailSuccess(response),
            error: (response) => this._handleResendActivationEmailError(response),
            type: "POST",
            url: route,
            data: { email: options.email }
        };
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, { settings: ajaxSettings });
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: "Resending Activation Email", content: "Please wait..." });
    }

    /**
     * Handle success response from resend activation email.
     */
    _handleResendActivationEmailSuccess(response)
    {
        Radio.channel("rodan").trigger(RODAN_EVENTS.EVENT__USER_RESENT_ACTIVATION_EMAIL);
    }

    /**
     * Handle error response from resend activation email.
     */
    _handleResendActivationEmailError(response)
    {
        const error = response.status === 400 ? "Invalid username." : "An error occured while resending activation email.";
        Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_ERROR, { content: error });
    }
}
