import Backbone from 'backbone';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Base model.
 */
export default class BaseModel extends Backbone.Model
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     *
     * @param {object} options initialization parameters for Backbone.Model
     */
    constructor(options)
    {
        super(options);
        this.on('change', (model, options) => this._onChange(model, options));
        this.on('sync', (model, response, options) => this._onSync(model, response, options));
    }

    /**
     * URL override to add trailing slash. Also, the URL will depend if this model instance has been saved or not. 
     * If not saved, we have to use the plural route for the model to save it.
     * That's the way Rodan works. :)
     *
     * @return {string} URL of Resource with trailing slash
     */
    url()
    {
        var original_url = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, this.routeName);
        if (typeof this.get('uuid') !== 'undefined')
        {
            original_url = this.get('url');
        }
        var parsed_url = original_url + ( original_url.charAt( original_url.length - 1 ) === '/' ? '' : '/' );
        return parsed_url;
    }

    /**
     * Override of destroy to allow for generic handling.
     *
     * @param {object} options Backbone.Model.destroy options object
     */
    destroy(options)
    {
        options = this._applyResponseHandlers(options);
        options.task = 'destroy';
        super.destroy(options);
    }

    /**
     * Override of save to allow for generic handling.
     *
     * @param {object} attributes attributes to change in model
     * @param {object} options Backbone.Model.save options object
     */
    save(attributes, options)
    {
        options = this._applyResponseHandlers(options);
        options.task = 'save';
        return super.save(attributes, options);
    }

    /**
     * Override of fetch to allow for generic handling.
     *
     * @param {object} options Backbone.Model.fetch options object
     */
    fetch(options)
    {
        options = this._applyResponseHandlers(options);
        options.task = 'fetch';
        super.fetch(options);
    }

    /**
     * Returns descriptive string for model. This should be overridden by sub-classes.
     *
     * @return {string} returns 'no description available' unless overridden by subclass
     */
    getDescription()
    {
        return 'no description available';
    }

    /**
     * Parses ID out of resource type URL.
     *
     * @param {string} url URL with UUID at end
     * @return {string} UUID
     * @todo this should be in a utility file
     */
    parseIdFromUrl(url)
    {
        var lastSlash = url.lastIndexOf('/');
        var subString = url.substring(0, lastSlash);
        var secondLastSlash = subString.lastIndexOf('/');
        return url.substring(secondLastSlash + 1, lastSlash);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * On change handler.
     */
    _onChange(model, response, options)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__MODEL_CHANGE, {model: model, options: options});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__MODEL_CHANGE + model.get('url'), {model: model, options: options});
    }

    /**
     * On sync handler.
     */
    _onSync(model, response, options)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__MODEL_SYNC, {model: model, response: response, options: options});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__MODEL_SYNC + model.get('url'), {model: model, response: response, options: options});
    }

    /**
     * Applies response handlers.
     */
    _applyResponseHandlers(options)
    {
        // Check if options are defined.
        if (options === undefined)
        {
            options = {};
        }

        // Success.
        var genericSuccessFunction = (model, response, options) => this._handleSuccessResponse(model, response, options);
        if (!options.hasOwnProperty('success'))
        {
            options.success = (model, response, options) => this._handleSuccessResponse(model, response, options);
        }
        else
        {
            var customSuccessFunction = options.success;
            options.success = function(model, response, options)
            {
                customSuccessFunction(model, response, options);
                genericSuccessFunction(model, response, options);
            };
        }

        // Error.
        var genericErrorFunction = (model, response, options) => this._handleErrorResponse(model, response, options);
        if (!options.hasOwnProperty('error'))
        {
            options.error = (model, response, options) => this._handleErrorResponse(model, response, options);
        }
        else
        {
            var customErrorFunction = options.error;
            options.error = function(model, response, options)
            {
                customErrorFunction(model, response, options);
                genericErrorFunction(model, response, options);
            };
        }

        return options;
    }

    /**
     * Handle success response.
     */
    _handleSuccessResponse(model, response, options)
    {
    }

    /**
     * Handle error response.
     */
    _handleErrorResponse(model, response, options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {model: model,
                                                                  response: response,
                                                                  options: options});
    }
}
BaseModel.prototype.idAttribute = 'uuid';