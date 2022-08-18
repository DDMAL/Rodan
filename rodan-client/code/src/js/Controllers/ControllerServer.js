import $ from 'jquery';
import Backbone from 'backbone';
import BaseController from 'js/Controllers/BaseController';
import Configuration from 'js/Configuration';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

var oldsync = Backbone.sync;
Backbone.sync = function(method, model, options) { 'use strict'; return oldsync(method, model, options); };

/**
 * Server controller.
 */
export default class ControllerServer extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this._serverDate = null;
        this._server = null;
        this._originalSync = Backbone.sync;
        this._responseTimeout = null;
        this._responsePanic = null;
        this._waitingEventTriggered = false;
        this._pendingRequests = 0;
        Backbone.sync = (method, model, options) => this._sync(method, model, options);
    }

    /**
     * AJAX prefilter associated with server control.
     *
     * This will count the pending responses and set timeouts.
     *
     * @param {object} options object.beforeSend (optional) is a function that takes in the XmlHTTPRequest before sending; this may be useful for doing pre-processing of AJAX requests
     */
    ajaxPrefilter(options)
    {
        var that = this;
        var oldOnBeforeSend = options.beforeSend;
        options.beforeSend = function (xhr) 
        {
            if (oldOnBeforeSend)
            {
                oldOnBeforeSend(xhr);
            }

            // Set a timeout for x seconds.
            if (that._responseTimeout === null)
            {
                that._responseTimeout = setTimeout(() => that._sendWaitingNotification(), Configuration.SERVER_WAIT_TIMER);
            }

            // Set a timeout for panic.
            if (that._responsePanic === null)
            {
                that._responsePanic = setTimeout(() => that._sendPanicNotification(), Configuration.SERVER_PANIC_TIMER);
            }

            // Increment pending requests.
            that._pendingRequests++;
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_REQUESTS_PENDING_UPDATE, {pending: that._pendingRequests});
        };
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Sends dummy request to get server time.
     */
    _sendTimeGetterRequest()
    {
        var request = new XMLHttpRequest();
        request.open('HEAD', Configuration.getServerURL());
        request.onreadystatechange = (event) => this._handleTimeRequest(event);
        request.setRequestHeader('Content-Type', 'text/html');
        request.send('');
    }

    /**
     * Sync override. We do this to add handlers.
     */
    _sync(method, model, options)
    {
        options = this._applyAJAXResponseHandlers(options);
        return this._originalSync(method, model, options);
    }

    /**
     * Event bindings.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_CONFIGURATION, () => this._handleRequestConfiguration());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_DATE, () => this._handleRequestDate());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_LOAD_ROUTES, () => this._getRoutes());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_LOAD_ROUTE_OPTIONS, () => this._handleGetRouteOptions());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, routeName => this._handleRequestServerRoute(routeName));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE_OPTIONS, options => this._handleRequestServerRouteOptions(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_GET_HOSTNAME, () => this._handleRequestServerHostname());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_GET_VERSION, () => this._handleRequestServerVersionRodan());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, (options) => this._handleRequestAjax(options));
    }

    /**
     * Return server config.
     */
    _handleRequestConfiguration()
    {
        return this._server.configuration;
    }

    /**
     * Return server date.
     */
    _handleRequestDate()
    {
        return this._serverDate;
    }

    /**
     * Returns associated route.
     */
    _handleRequestServerRoute(routeName)
    {
        return this._server.routes[routeName].url;
    }

    /**
     * Returns associated route options.
     */
    _handleRequestServerRouteOptions(options)
    {
        return this._server.routes[options.route].options;
    }

    /**
     * Returns server hostname.
     */
    _handleRequestServerHostname()
    {
        return Configuration.SERVER_HOST;
    }

    /**
     * Returns server version - Rodan.
     */
    _handleRequestServerVersionRodan()
    {
        return this._server.version;
    }

    /*
    * Fetches the routes from the Rodan server. This is the first function to be called in the
    * Rodan loading process. It hits the root endpoint on the Rodan server and from there downloads
    * all of the path endpoints required to automatically configure the client application.
    * */
    _getRoutes()
    {
        var routeRequest = new XMLHttpRequest();

        // FYI: the use of the Fat arrow maps `this` to `ServerController`, not the request object.
        routeRequest.onload = (event) =>
        {
            if (routeRequest.responseText && routeRequest.status === 200)
            {
                this._server = JSON.parse(routeRequest.responseText);
                for (var routeName in this._server.routes)
                {
                    this._server.routes[routeName] = {url: this._server.routes[routeName]};
                }
                Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_ROUTESLOADED);
            }
            else
            {
                console.error('Routes could not be loaded from the server.');
                console.error(event);
            }
        };

        routeRequest.open('GET', Configuration.getServerURL(), true);
        routeRequest.setRequestHeader('Accept', 'application/json');
        routeRequest.send();
    }

    /**
     * Fetches the OPTIONS (arguments for sorting, filtering, etc).
     */
    _handleGetRouteOptions()
    {
        for (var key in this._server.routes)
        {
            // Skip routes that don't have any options.
            if (Configuration.ROUTES_WITHOUT_OPTIONS.indexOf(key) >= 0)
            {
                continue;
            }

            var ajaxSettings = {success: (result, status, xhr) => this._handleGetRouteOptionsSuccess(result, status, xhr),
                                type: 'OPTIONS',
                                url: this._server.routes[key].url,
                                dataType: 'json'};
            ajaxSettings = this._applyAJAXResponseHandlers(ajaxSettings);
            var request = $.ajax(ajaxSettings);
            request.key = key;
        }
    }

    /**
     * Handle get route options success.
     */
    _handleGetRouteOptionsSuccess(result, status, xhr)
    {
        this._server.routes[xhr.key].options = result;
    }

    /**
     * Apply success/error AJAX handlers to HTTP request.
     */
    _applyAJAXResponseHandlers(options)
    {
        var genericResponseFunction = (result, status, xhr) => this._handleAJAXResponse(result, status, xhr);

        // Success.
        if (!options.hasOwnProperty('success'))
        {
            options.success = genericResponseFunction;
        }
        else
        {
            var customSuccessFunction = options.success;
            options.success = function(result, status, xhr)
            {
                customSuccessFunction(result, status, xhr);
                genericResponseFunction(result, status, xhr);
            };
        }

        // Error
        if (!options.hasOwnProperty('error'))
        {
            options.error = genericResponseFunction;
        }
        else
        {
            var customErrorFunction = options.error;
            options.error = function(result, status, xhr)
            {
                customErrorFunction(result, status, xhr);
                genericResponseFunction(result, status, xhr);
            };
        }

        return options;
    }

    /**
     * Handle AJAX response (generic).
     */
    _handleAJAXResponse(result, status, xhr)
    {
        // Decrement the pending requests.
        this._pendingRequests--;
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_REQUESTS_PENDING_UPDATE, {pending: this._pendingRequests});

        if (document.readyState === 'complete' && this._pendingRequests === 0)
        {
            clearTimeout(this._responseTimeout);
            clearTimeout(this._responsePanic);
            this._responseTimeout = null;
            this._responsePanic = null;
            if (this._waitingEventTriggered)
            {
                this._sendIdleNotification();
            }
        }
        else if (this._waitingEventTriggered)
        {
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_WAITING, {pending: this._pendingRequests});
        }

        // Get the time.
        if (xhr.getResponseHeader)
        {
            var dateResponse = new Date(xhr.getResponseHeader('Date'));
            if (this._serverDate === null || this._serverDate.getTime() < dateResponse.getTime())
            {
                this._updateServerDate(dateResponse);
                clearInterval(this._timeGetterInterval);
                this._timeGetterInterval = null;
            }
        }

        // Set Date getter interval.
        if (!this._timeGetterInterval)
        {
            this._timeGetterInterval = setInterval(() => this._sendTimeGetterRequest(), Configuration.SERVER_REQUEST_TIME_INTERVAL);
        }
    }


    /**
     * Sends a notification that queries are still pending.
     */
    _sendWaitingNotification()
    {
        this._waitingEventTriggered = true;
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_WAITING, {pending: this._pendingRequests});
    }

    /**
     * Send idle notification.
     */
    _sendIdleNotification()
    {
        this._waitingEventTriggered = false;
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_IDLE);
    }

    /**
     * Sends a panic notification
     */
    _sendPanicNotification()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_PANIC);
    }

    /**
     * Handle time getter request response.
     */
    _handleTimeRequest(event)
    {
        var request = event.currentTarget;
        if (request && request.getResponseHeader('Date'))
        {
            var dateResponse = new Date(request.getResponseHeader('Date'));
            if (this._serverDate === null || this._serverDate.getTime() < dateResponse.getTime())
            {
                this._updateServerDate(dateResponse);
            }
        }
    }

    /**
     * Updates recorded server date.
     */
    _updateServerDate(date)
    {
        this._serverDate = date;
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__SERVER_DATE_UPDATED, {date: this._serverDate});
    }

    /**
     * Requests custom AJAX request.
     */
    _handleRequestAjax(options)
    {
        var ajaxSettings = this._applyAJAXResponseHandlers(options.settings);
        $.ajax(ajaxSettings);
    }
}