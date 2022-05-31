import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import ViewLogin from './Login/ViewLogin';

/**
 * Layout view for main work area. This is responsible for loading views within the main region.
 */
export default class LayoutViewMain extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this.addRegions({
            region: 'div'
        });
        this._initializeRadio();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, options => this._handleCommandShow(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGOUT_SUCCESS, () => this._handleDeauthenticationSuccess());
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGINREQUIRED, () => this._handleAuthenticationLoginRequired());
    }

    /**
     * Handles request for login.
     */
    _handleAuthenticationLoginRequired()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: new ViewLogin()});
    }

    /**
     * Handle show.
     */
    _handleCommandShow(options)
    {
        /** @ignore */
        this.showChildView('region', options.view);
    }

    /**
     * Handle deauthentication success.
     */
    _handleDeauthenticationSuccess()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: new ViewLogin()});
    }
}
LayoutViewMain.prototype.template = _.template($('#template-empty').text());
