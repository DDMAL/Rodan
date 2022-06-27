import _ from 'underscore';
import $ from 'jquery';
import bootstrap from 'bootstrap';
import Marionette from 'backbone.marionette';
import moment from 'moment';
import Radio from 'backbone.radio';

import BehaviorTable from './Behaviors/BehaviorTable';
import ControllerAuthentication from './Controllers/ControllerAuthentication';
import ControllerContextMenu from './Controllers/ControllerContextMenu';
import ControllerDownload from './Controllers/ControllerDownload';
import ControllerModal from './Controllers/ControllerModal';
import ControllerProject from './Controllers/ControllerProject';
import ControllerResource from './Controllers/ControllerResource';
import ControllerResourceList from './Controllers/ControllerResourceList';
import ControllerRunJob from './Controllers/ControllerRunJob';
import ControllerServer from './Controllers/ControllerServer';
import ControllerUserPreference from './Controllers/ControllerUserPreference';
import ControllerWorkflow from './Controllers/ControllerWorkflow';
import ControllerWorkflowBuilder from './Controllers/ControllerWorkflowBuilder';
import ControllerWorkflowJob from './Controllers/ControllerWorkflowJob';
import ControllerWorkflowJobGroup from './Controllers/ControllerWorkflowJobGroup';
import ControllerWorkflowRun from './Controllers/ControllerWorkflowRun';
import Configuration from './Configuration';
import ErrorManager from 'js/Managers/ErrorManager';
import RODAN_EVENTS from './Shared/RODAN_EVENTS';
import GlobalInputPortTypeCollection from './Collections/Global/GlobalInputPortTypeCollection';
import GlobalJobCollection from './Collections/Global/GlobalJobCollection';
import GlobalOutputPortTypeCollection from './Collections/Global/GlobalOutputPortTypeCollection';
import GlobalProjectCollection from './Collections/Global/GlobalProjectCollection';
import GlobalResourceTypeCollection from './Collections/Global/GlobalResourceTypeCollection';
import GlobalResourceLabelCollection from './Collections/Global/GlobalResourceLabelCollection';
import LayoutViewMaster from './Views/Master/LayoutViewMaster';
import UpdateManager from './Managers/UpdateManager';
import TransferManager from './Managers/TransferManager';

/**
 * Main application class.
 */
export default class Application extends Marionette.Application
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Called on Marionette.Application.start(). This will load the configuration from the host.
     */
    onStart()
    {
        Configuration.load('configuration.json', () => this._startUp());
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Application start-up
     */
    _startUp()
    {
        // Check debug.
        if (Configuration.DEBUG)
        {
            Radio.tuneIn('rodan');
        }

        Configuration.load('info.json');

        // Non-network and non-GUI inits. Do these first.
        this._initializeDateTimeFormatter();
        this._initializeRadio();
        this._initializeCollections();
        this._initializeManagers();

        this._initializeAjaxPrefilters();
        this._initializeViews();
        this._initializeControllers();

        require('./.plugins');

        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_LOAD_ROUTES);
    }

    /**
     * Initialize managers.
     */
    _initializeManagers()
    {
        this._transferManager = new TransferManager();
        this._updateManager = new UpdateManager();
        // This is commented out because deleting a workflowRun throws a null error despite the error
        // being non-existent. Its errors are not very useful anyway. Fix in progress, see issue 475 (Rodan).
        // this._errorManager = new ErrorManager();
    }

    /**
     * Initializes various helpers.
     */
    _initializeDateTimeFormatter()
    {
        moment.defaultFormat = Configuration.DATETIME_FORMAT;
        _.formatFromUTC = function(dateTime)
        {
            // TODO - see https://github.com/DDMAL/rodan-client/issues/59
            try
            {
                return moment(dateTime).format();
            }
            catch(error)
            {
                return moment.moment(dateTime).format();
            }
        };
    }

    /**
     * Set event binding.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__SERVER_ROUTESLOADED, () => this._handleEventRoutesLoaded());
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__AUTHENTICATION_LOGIN_SUCCESS, () => this._handleAuthenticationSuccess());
    }

    /**
     * Initialize controllers. These are not used for viewing; rather, they are server/auth control.
     */
    _initializeControllers()
    {
        this._contextMenuController = new ControllerContextMenu();
        this._downloadController = new ControllerDownload();
        this._controllerServer = new ControllerServer();
        this._controllerAuthentication = new ControllerAuthentication(this._controllerServer);
        this._modalController = new ControllerModal();
        this._projectController = new ControllerProject();
        this._resourceController = new ControllerResource();
        this._resourceListController = new ControllerResourceList();
        this._runJobController = new ControllerRunJob();
        this._userPreferenceController = new ControllerUserPreference();
        this._workflowController = new ControllerWorkflow();
        this._workflowRunController = new ControllerWorkflowRun();
        this._workflowBuilderController = new ControllerWorkflowBuilder();
        this._workflowJobController = new ControllerWorkflowJob();
        this._workflowJobGroupController = new ControllerWorkflowJobGroup();
    }

    /**
     * Initialize AJAX prefilters. This allows the application a lower level of request monitoring (if desired).
     */
    _initializeAjaxPrefilters()
    {
        var that = this;
        $.ajaxPrefilter(function(options)
        {
            that._controllerAuthentication.ajaxPrefilter(options);
            that._controllerServer.ajaxPrefilter(options);
        });
    }

    /**
     * Initialize collections.
     */
    _initializeCollections()
    {
        this._jobCollection = new GlobalJobCollection();
        this._resourceTypeCollection = new GlobalResourceTypeCollection();
        this._inputPortTypeCollection = new GlobalInputPortTypeCollection();
        this._outputPortTypeCollection = new GlobalOutputPortTypeCollection();
        this._projectCollection = new GlobalProjectCollection();
        this._resourceLabelCollection = new GlobalResourceLabelCollection();
    }

    /**
     * Initialize all the views so they can respond to events.
     */
    _initializeViews()
    {
        this._layoutViewMaster = new LayoutViewMaster();
    }

    /**
     * Handle EVENT__SERVER_ROUTESLOADED.
     */
    _handleEventRoutesLoaded()
    {
        // Render layout views.
        /** @ignore */
        this.showView(this._layoutViewMaster);

        // Do version compatibility trimming.
        if (Configuration.ENFORCE_VERSION_COMPATIBILITY)
        {
            RODAN_EVENTS.enforceVersionCompatibility();
        }

        // Check authentication.
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_CHECK);
    }

    /**
     * Handle authentication success.
     */
    _handleAuthenticationSuccess()
    {
        var user = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_USER);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_LOAD_ROUTE_OPTIONS);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_PROJECTS_LOAD, {data: {user: user.get('uuid')}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_INPUTPORTTYPES_LOAD);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_OUTPUTPORTTYPES_LOAD);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPES_LOAD);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABELS_LOAD);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOBS_LOAD, {data: {enabled: 'True'}});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_SELECTED_COLLECTION);
    }
}
Application.prototype.region = '#region-master';
