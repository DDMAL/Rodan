import $ from 'jquery';
import Radio from 'backbone.radio';
import RODAN_EVENTS from './Shared/RODAN_EVENTS';

/**
 * Client configuration object.
 */
var Configuration = {
///////////////////////////////////////////////////////////////////////////////////////
// Server parameters
///////////////////////////////////////////////////////////////////////////////////////
    // Host of server (e.g. 123.456.789.0 or mydomain.com).
    SERVER_HOST: '',

    // Server port. Default is 443.
    SERVER_PORT: 443,

    SERVER_HTTPS: true,
    // Set to true if using HTTPS (else HTTP). Default is true.

    // Set to true if the server allows socket connections. Default is true.
    SERVER_SOCKET_AVAILABLE: true,

    SERVER_SOCKET_DEBUG: false,
    // Set to true if you want to see socket message data in the console. Default is false.

    // Authentication type. Either 'session' or 'token'. Default is 'token'.
    SERVER_AUTHENTICATION_TYPE: 'token',

    // This determines the method to use for loading updates from the server.
    // Either 'POLL' (default) or 'SOCKET'.
    SERVER_UPDATE_METHOD: 'POLL',

    // Interval after which the client will get the server time (ms).
    // Generally, the client extracts the server time from all responses from the server.
    // However, if the client has not received a response from the server after this
    // amount of time, the client will fire an HTTP HEAD request and get the server 
    // time. This means that the server MUST exposde the 'Date' response header. As
    // such, it is recommended that this value be greater than the 
    // EVENT_TIMER_FREQUENCY to reduce traffic.
    SERVER_REQUEST_TIME_INTERVAL: 60000,

    // Milliseconds to wait before the client goes into a 'wait' mode. This is used in the WorkflowBuilder when heavy lifting is going on, such as a Workflow import.
    SERVER_WAIT_TIMER: 500,

    // Milliseconds to wait before the client 'panics' mode. This is used in the WorkflowBuilder when heavy lifting is going on, such as a Workflow import.
    // This should be bigger than SERVER_WAIT_TIMER.
    SERVER_PANIC_TIMER: 8000,

///////////////////////////////////////////////////////////////////////////////////////
// General behavior parameters
///////////////////////////////////////////////////////////////////////////////////////
    // URL for website.
    WEBSITE_URL: 'http://ddmal.github.io/rodan-client/',

    // Date/time format. See http://momentjs.com/docs/#/displaying/format/
    DATETIME_FORMAT: 'YYYY-MM-DD HH:mm:ss',

    // Event timer frequency (ms).
    EVENT_TIMER_FREQUENCY: 3000,

    // If you have a Job package meant solely for distributing Resources (i.e. takes in a single Resource and outputs that Resource) you have the option to use a 
    // feature that will automatically create a WorkflowJob of the correct Job that satisfies selected InputPorts. If this is the case, those Jobs must have
    // their category set to the value of RESOURCE_DISTRIBUTOR_CATEGORY.
    RESOURCE_DISTRIBUTOR_CATEGORY: 'Resource Distributor',

///////////////////////////////////////////////////////////////////////////////////////
// Interactive RunJob parameters
///////////////////////////////////////////////////////////////////////////////////////
    // Time (in milliseconds) that the CLIENT will attempt to hold a job.
    RUNJOB_ACQUIRE_DURATION: 3600000,

    // Interval (in milliseconds) that the RunJob controller will use to reacquire interactive locks.
    RUNJOB_ACQUIRE_INTERVAL: 5000,

///////////////////////////////////////////////////////////////////////////////////////
// DON'T EDIT BELOW THIS LINE (unless you know what you're doing)
///////////////////////////////////////////////////////////////////////////////////////
    // Routes without OPTIONS. if the route name is in here, the client won't try to grab them.
    ROUTES_WITHOUT_OPTIONS: ['auth-reset-token', 'taskqueue-status', 'auth-change-password', 'auth-register', 'taskqueue-scheduled', 'taskqueue-active', 'auth-token'],

    // Client admin info. Leave fields empty if you don't want to be bothered. ;)
    ADMIN_CLIENT: {
        NAME: '',
        EMAIL: ''
    },

    // Turns on debug mode.
    DEBUG: false,

    // Disables features that require a later version of Rodan iff true.
    // It's useful to turn this to 'false' if implementing something new.
    ENFORCE_VERSION_COMPATIBILITY: true,

    // Created to hold info on plugins. 
    PLUGINS: []
};

///////////////////////////////////////////////////////////////////////////////////////
// Loader methods
///////////////////////////////////////////////////////////////////////////////////////
/**
 * Convenience method to return the URL (I.e. '<http or https>://SERVER_HOST:SERVER_PORT'.)
 *
 * @return {string} <http or https>://SERVER_HOST:SERVER_PORT
 */
Configuration.getServerURL = function()
{
    var url = this.SERVER_HOST + ':' + this.SERVER_PORT;
    return this.SERVER_HTTPS ? 'https://' + url : 'http://' + url;
};

/**
 * Requests filename from the client host. Whatever it gets from the host
 * it will merge with the default configuration.
 *
 * When finished it will fire the provided callback.
 */
Configuration.load = function(filename, callback)
{
    'use strict';
    var request = new XMLHttpRequest();
    request.open('GET', filename, true);
    request.onreadystatechange = (event) => this._handleStateChange(event, filename, callback);
    request.send();
};

/**
 * Handle state change of request.
 */
Configuration._handleStateChange = function(event, filename, callback)
{
    'use strict';
    var request = event.currentTarget;
    switch (request.readyState)
    {
        case 0: //UNSENT
        {
            break;
        }

        case 1: //OPENED
        {
            break;
        }

        case 2: //HEADERS_RECEIVED
        {
            break;
        }

        case 3: //LOADING
        {
            break;
        }

        case 4:
        {
            var configuration = JSON.parse(request.response);
            $.extend(this, configuration);
            Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__CONFIGURATION_LOADED);
            if (callback)
            {
                callback();
            }
            break;
        }

        default:
        {
            // TODO error
            console.error('failed to load file ' + filename);
            break;
        }
    }
};

export default Configuration;
