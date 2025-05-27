import BaseCollection from 'js/Collections/BaseCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Global Collections that should be loaded on startup. These are not expected to change during the lifetime of a session. They are also customized to get non-paginated results.
 */
export default class GlobalCollection extends BaseCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options initialization parameters for Backbone.Collection
     * @throws {Error} thrown if called more than once
     */
     initialize(options)
     {
        super.initialize(options);
        this._allowPagination = false;
     }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(this._loadCommand, options => this._retrieveCollection(options));
        Radio.channel('rodan').reply(this._requestCommand, () => this._handleRequestInstance());
    }

    /**
     * Returns this instance.
     *
     * @return {GlobalCollection} this instance
     */
    _handleRequestInstance()
    {
        return this;
    }

    /**
     * Retrieves collection.
     */
    _retrieveCollection(options)
    {
        options = options ? options : {};
        this.reset();
        var data = options.hasOwnProperty('data') ? options.data : {};
        if (!this._allowPagination)
        {
            data.disable_pagination = true;
        }
        options.data = data;
        /** @ignore */
        this.url = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, this._route);
        this.fetch(options);
    }
}
