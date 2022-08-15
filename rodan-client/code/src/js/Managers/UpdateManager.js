import Configuration from 'js/Configuration';
import PollUpdater from 'js/Updater/PollUpdater';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import SocketUpdater from 'js/Updater/SocketUpdater';

/**
 * This manages how updates are handled.
 */
export default class UpdateManager
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor()
    {
        this._updater = null;
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__CONFIGURATION_LOADED, () => this._handleEventConfigurationLoaded());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, (options) => this._handleRequestUpdateSetFunction(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__UPDATER_CLEAR, () => this._handleRequestUpdateClear());
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle config load. Reads the configuration and check for socket setting.
     */
    _handleEventConfigurationLoaded()
    {
        if (Configuration.SERVER_SOCKET_AVAILABLE)
        {
            this._updater = new SocketUpdater();
        }
        else
        {
            this._updater = new PollUpdater({frequency: Configuration.EVENT_TIMER_FREQUENCY});
        }
    }

    /**
     * Handle request Update set function.
     */
    _handleRequestUpdateSetFunction(options)
    {
        this._updater.setCollections(options.collections);
    }

    /**
     * Handle request Update clear.
     */
    _handleRequestUpdateClear(options)
    {
        this._updater.clear();
    }
}