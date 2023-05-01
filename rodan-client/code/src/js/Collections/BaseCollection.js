import $ from 'jquery';
import _ from 'underscore';
import Backbone from 'backbone';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Pagination from 'js/Models/Pagination';
import Radio from 'backbone.radio';

/**
 * Subclass of Backbone.Collection.
 *
 * Some functionality of Backbone.Collection is overridden to facilitate server-based pagination, filtering, and sorting.
 */
export default class BaseCollection extends Backbone.Collection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     *
     * @param {object} options initialization parameters for Backbone.Collection
     */
    constructor(options)
    {
        super(options);
        this._pagination = new Pagination();
        this._lastData = {};
        this._initializeRadio();
        this._filters = {};
        this._sort = {};//{ordering: '-created'};
        this._page = {};
        this._enumerations = this._enumerations ? this._enumerations : new Map();
        this.on('add', (model, collection, options) => this._onAdd(model, collection, options));
    }

    /**
     * Returns route.
     *
     * @return {string} route
     */
    get route()
    {
        return this._route;
    }

    /**
     * Returns enumerations of this Collection. These are custom-defined in the subclasses.
     *
     * Enumerations should be defined in subclasses as ES6 Maps. The key is a property of
     * the associated Model in the Collection. The value is an Object:
     *
     * - {label: string, values: [{value: primitive type, label: string}] (optional)}
     *
     * In the above:
     * - "label" is a string that will appear in the table header
     * - "values" is optional; populate this array with explicit "value"/"label"s if desired, else BaseCollection will determine the values for enumeration based on the contents of the Collection
     *
     * @todo Rodan server should provide explicit enumerations
     *
     * @return Map enumerations
     */
    getEnumerations()
    {
        return this._enumerations;
    }

    /**
     * Parse results.
     *
     * @param {object} response JSON object
     * @return {object} JSON object
     */
    parse(response)
    {
        if (response.count)
        {
            this._parsePagination(response);
        }

        if (this._enumerations && this._enumerations.size > 0)
        {
            this._populateEnumerations(response);
        }

        if (response.hasOwnProperty('results'))
        {
            return response.results;
        }
        return response;
    }

    /**
     * Parses ID out of URL.
     *
     * @param {string} url URL
     * @return {string} string representing UUID of Collection
     * @todo this should be moved to a utility class
     */
    parseIdFromUrl(url)
    {
        var lastSlash = url.lastIndexOf('/');
        var subString = url.substring(0, lastSlash);
        var secondLastSlash = subString.lastIndexOf('/');
        return url.substring(secondLastSlash + 1, lastSlash);
    }

    /**
     * Override of fetch to allow for generic handling.
     *
     * Note that we save the data options. This is in case we do a create
     * and have to reload/fetch the previous collection. We need to preserve
     * the fetch parameters.
     *
     * @param {object} options Backbone.Collection.fetch options object
     */
    fetch(options)
    {
        if (!options)
        {
            options = {};
        }

        // Set task.
        options.task = 'fetch';

        // Save last data.
        this._lastData = options.data ? options.data : {};

        // Build final options.
        var finalOptions = {};
        if (options.error)
        {
            finalOptions.error = options.error;
        }
        if (options.success)
        {
            finalOptions.success = options.success;
        }
        if (options.hasOwnProperty("async")) {
            finalOptions.async = options.async;
        }
        finalOptions.reset = options.reset ? options.reset : false;
        finalOptions.traditional = true;
        finalOptions.data = {};
        $.extend(finalOptions.data, this._filters);
        $.extend(finalOptions.data, this._sort);
        $.extend(finalOptions.data, this._page);
        $.extend(finalOptions.data, options.data);

        // Fech.
        super.fetch(finalOptions);
    }

    /**
     * Override of create.
     *
     * This override exists because we do NOT want to add it to the collection
     * by default (as there's a limit to what the server returns for collections,
     * and we need to respect that). However, if the save worked, we do want to do a fetch
     * to update the Collection. The fetch is called in the custom success handler for creation.
     *
     * There's also the case if this Collection is local and not associated with a DB Collection.
     *
     * @param {object} options Backbone.Collection.create options object
     * @return {Backbone.Model} instance of Backbone.Model or subclass of Backbone.Model
     */
    create(options)
    {
        var instance = new this.model(options);
        if (this.hasOwnProperty('url'))
        {
            instance.save({}, {success: () => this._handleCreateSuccess()});
        }
        else
        {
            instance.save({}, {success: (model) => this.add(model)});
        }
        return instance;
    }

    /**
     * Requests a sorted fetch. This is not called "sort" because backbone already has
     * a sort method for the Collection.
     *
     * If no options.data is passed, the options.data from the last fetch are used.
     *
     * @param {boolean} ascending results will return in ascending order if true
     * @param {string} field name of field to sort by
     * @param {object} options Backbone.Collection.fetch options object
     */
    fetchSort(ascending, field, options)
    {
        if (options && options.data)
        {
            this._lastData = options.data;
        }
        this._sort.ordering = field;
        if (!ascending)
        {
            this._sort.ordering = '-' + field;
        }
        this.fetch({data: this._lastData, reset: true});
    }

    /**
     * Requests a filtered fetch.
     *
     * If no options.data is passed, the options.data from the last fetch are used.
     *
     * @param {array} filters array of objects; {name: string, value: primitive}; what filters can be used is defined in Rodan
     * @param {object} options Backbone.Collection.fetch options object
     * @todo give more info on filters
     */
    fetchFilter(filters, options)
    {
        if (options && options.data)
        {
            this._lastData = options.data;
        }
        this._filters = filters;
        this._page = {};
        this.fetch({data: this._lastData, reset: true});
    }

    /**
     * Requests a page to be fetched.
     *
     * If no options.data is passed, the options.data from the last fetch are used.
     *
     * @param {integer} page non-negative page number to retrieve from server
     * @param {object} options Backbone.Collection.fetch options object
     */
    fetchPage(page, options)
    {
        if (options && options.data)
        {
            this._lastData = options.data;
        }
        this._page = page;
        this.fetch({data: this._lastData, reset: true});
    }

    /**
     * Returns pagination object for this Collection.
     *
     * @return {object} pagination object
     * @todo point to pagination info on Rodan server
     */
    getPagination()
    {
        return this._pagination;
    }

    /**
     * Returns the URL associated with this Collection.
     *
     * @return {string} URL associated with this Collection
     */
    url()
    {
        return Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, this._route);
    }

    /**
     * Syncs the Collection while preserving the last used fetch options.data.
     */
    syncCollection()
    {
        this.fetch({data: this._lastData});
    }

    swapItems(index1, index2)
    {
        if (index1 !== index2) {
            var models = this.models.slice();
            models[index1] = models.splice(index2, 1, models[index1])[0];
            this.set(models);
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        // dummy
    }

    /**
     * Handles a succesful creation. All this does is "properly" reload the collection.
     */
    _handleCreateSuccess()
    {
        this.syncCollection({});
    }

    /**
     * Parses pagination parameters from response.
     */
    _parsePagination(options)
    {
        this._pagination.set({'count': options.count,
                              'next': options.next !== null ? options.next : '#',
                              'previous': options.previous !== null ? options.previous : '#',
                              'current': options.current_page,
                              'total': options.total_pages});
    }

    /**
     * Populates enumerations.
     */
    _populateEnumerations(response)
    {
        var options = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE_OPTIONS, {route: this.route});
        var items = response.results ? response.results : response;
        for (var [field, enumeration] of this._enumerations)
        {
            // If no enumerations, let's try to populate via routes. If that doesn't work, auto-populate.
            if (!enumeration.values || enumeration.values.length === 0)
            {
                enumeration.values = [];

                // Check if enumerations in 'OPTIONS' from server.
/*                if (options.filter_fields[field] && options.filter_fields[field].length > 0)
                {
                    for (var i in options.filter_fields[field])
                    {
                        var result = options.filter_fields[field][i];
                        enumeration.values.push({value: result, label: result});
                    }
                    enumeration.values = _.uniq(enumeration.values, false, function(item) {return item.value;});
                }
                else
*/                {
                    for (var i in items)
                    {
                        var result = items[i];
                        enumeration.values.push({value: result[field], label: result[field]});
                    }
                    enumeration.values = _.uniq(enumeration.values, false, function(item) {return item.value;});
                }

                // Sort.
                enumeration.values.sort(function (a, b)
                {
                    if (a.label > b.label)
                    {
                        return 1;
                    }
                    else if (a.label < b.label)
                    {
                        return -1;
                    }
                    return 0;
                });
            }
        }
    }

    /**
     * Handle backbone add event.
     */
    _onAdd(model, collection, options)
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__COLLECTION_ADD, {model: model, collection: collection, options: options});
    }
}
