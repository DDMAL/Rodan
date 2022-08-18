import AbstractUpdater from './AbstractUpdater';
import Configuration from 'js/Configuration';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * Updater that uses sockets to trigger collection updates.
 */
export default class SocketUpdater extends AbstractUpdater
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor()
    {
        super();
	    var protocol = Configuration.SERVER_HTTPS ? 'wss' : 'ws';
        this._webSocket = new WebSocket(protocol + '://' + Configuration.SERVER_HOST + ':' + Configuration.SERVER_PORT + '/ws/rodan?subscribe-broadcast&publish-broadcast&echo');
        this._webSocket.onmessage = (event) => this._handleSocketMessage(event);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle login success.
     */
    _handleEventLogoutSuccess()
    {
        this._webSocket.close();
    }

    /**
     * Handle socket message.
     */
    _handleSocketMessage(event)
    {
        // Output if debug socket.
        if (Configuration.SERVER_SOCKET_DEBUG)
        {
            console.log(event.data);
        }

        // Process.
        if (event.data === '--heartbeat--')
        {
          //  this._processHeartbeat(event);
        }
        else
        {
            this._processSocketMessage(JSON.parse(event.data));
        }
    }

    /**
     * Process socket message.
     */
    _processSocketMessage(data)
    {
        // We definitely update if:
        //
        // - no model is specified
        // - the model specified is a Project
        //
        // In these cases, the update is very general.
        // Else, we have to check if the model is related to our active project somehow.
        if (!data.model || data.model === 'project' || !data.project)
        {
            this.update();
        }
        else if (data.project)
        {
            var activeProject = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
            if (activeProject && data.project === activeProject.id)
            {
                this.update();
            }
        }
    }
}
