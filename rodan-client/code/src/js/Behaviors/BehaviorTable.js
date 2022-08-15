import $ from 'jquery';
import _ from 'underscore';
import datetimepicker from 'eonasdan-bootstrap-datetimepicker';
import 'jqueryui';
import BaseCollection from 'js/Collections/BaseCollection';
import Configuration from 'js/Configuration';
import Environment from 'js/Shared/Environment';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * A Marionette Behavior for tables. This class defines sorting and filtering.
 */
export default class BehaviorTable extends Marionette.Behavior
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this._filtersInjected = false;
        this._datetimepickerElements = [];
        this._lastTarget = null;
        this._multipleSelectionKey = Environment.getMultipleSelectionKey();
        this._rangeSelectionKey = Environment.getRangeSelectionKey();
    }

    /**
     * Delegate events and inject table controls after render.
     *
     * @param {Marionette.View} view View from which the Behavior will get events
     */
    onRender(view)
    {
        // Not really pretty, but works for now. Marionette calls 'delegateEvents'
        // before our custom 'initialize' on the view. However, at that point, the
        // collection is not yet set in the view, so binding doesn't work. This next
        // line is a work around.
        // TODO - fix/find better way
        this.view.delegateEvents();

        // Inject controls and initialize.
        this._injectControl();
        this._processPagination(null);

        // Inject the controls.
        if (view.collection)
        {
            this._handleCollectionEventSync(view.collection);
        }
        
        if (view.collection._route === "projects")
        {
            Radio.channel('rodan').on(RODAN_EVENTS.REQUEST__NAVIGATION_PAGINATION_FIRST, () => this._handlePaginationFirst());
            Radio.channel('rodan').on(RODAN_EVENTS.REQUEST__NAVIGATION_PAGINATION_PREVIOUS, () => this._handlePaginationPrevious());
            Radio.channel('rodan').on(RODAN_EVENTS.REQUEST__NAVIGATION_PAGINATION_NEXT, () => this._handlePaginationNext());
            Radio.channel('rodan').on(RODAN_EVENTS.REQUEST__NAVIGATION_PAGINATION_LAST, () => this._handlePaginationLast());
        }
    }

    /**
     * Destroy instance. This takes care of destroying any known DateTimePicker instances before moving to the next View.
     * Also reset last target.
     */
    onDestroy()
    {
        var datetimePickerElementIds = $(this.el).find(':data(DateTimePicker)').map(function(){return $(this).attr('id');}).get();
        for (var index in datetimePickerElementIds)
        {
            $(this.el).find('#' + datetimePickerElementIds[index]).data('DateTimePicker').destroy();
        }
        this._lastTarget = null;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - injectors
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Injects control template.
     */
    _injectControl()
    {
        if (this.$el.find('.table-control').length === 0)
        {
            this.$el.find('div.table-responsive').before($(this.options.templateControl).html());
        }
    }

    /**
     * Returns the filters for the associated Collection.
     */
    _getFilters(collection, filterFields)
    {
        // Some tables will be defined with enumerations.
        var enumerations = collection.getEnumerations();

        // Get all columns that have a data-name attribute.
        var filters = [];
        this._datetimepickerElements = [];
        var columns = $(this.el).find(this.options.table + ' thead th').filter(function() { return $(this).attr('data-name'); });
        // Create a mapping of column name to column title.
        var columnTitlesAndNames = columns.map(function() {
           return {[$(this).attr('data-name')]: $(this).text()}
        });
        var columnTitleByName = Object.assign({}, ...columnTitlesAndNames.get());
        var filterTitles = this.view.filterTitles || {};

        for (var [field, fieldFilters] of Object.entries(filterFields))
        {
            var datetimeLtFilter = false;
            var datetimeGtFilter = false;
            // Try to find a title for the filter - either specified in the view class, or taken
            // from the corresponding column title.
            var filterTitle = filterTitles[field] || columnTitleByName[field];
            if (filterTitle)
            {
                // First, check to see if this is an enumeration field (which Django doesn't cover).
                // If it is, deal with it as such.
                for (var filter of fieldFilters)
                {
                    switch (filter)
                    {
                        case 'icontains':
                        {
                            filters.push(this._getFilterText(filterTitle, field));
                            break;
                        }

                        case 'gt':
                        {
                            datetimeGtFilter = true;
                            break;
                        }

                        case 'lt':
                        {
                            datetimeLtFilter = true;
                            break;
                        }

                        case 'exact':
                        {
                            if (field === 'labels')
                            {
                                filters.push(this._getFilterLabels(filterTitle, field));
                            }
                            break;
                        }

                        default:
                        {
                            break;
                        }
                    }
                }

                // Check for datetime filters.
                if (datetimeGtFilter || datetimeLtFilter)
                {
                    if (datetimeGtFilter)
                    {
                        var elementId = '#' + field + '__gt';
                        this._datetimepickerElements.push(elementId);
                    }
                    if (datetimeLtFilter)
                    {
                        elementId = '#' + field + '__lt';
                        this._datetimepickerElements.push(elementId);
                    }
                    filters.push(this._getFilterDatetime(filterTitle, field));
                }
            }
        }

        // Finally, get enumerations.
        var templateChoice = _.template($(this.options.templateFilterChoice).html());
        var templateInput = _.template($(this.options.templateFilterEnum).html());
        for (var [field, enumeration] of enumerations)
        {
            var htmlChoice = templateChoice({label: enumeration.label, field: field});
            var htmlInput = templateInput({label: enumeration.label, field: field, values: enumeration.values});
            var filterObject = {collectionItem: htmlChoice, input: htmlInput};
            filters.push(filterObject);
        }

        return filters;
    }

    /**
     * Injects filtering functionality into template.
     */
    _injectFiltering(filterFields)
    {
        var filters = this._getFilters(this.view.collection, filterFields);
        for (var index in filters)
        {
            var $collectionItem = $(filters[index].collectionItem);
            var $formInput = $(filters[index].input);
            $collectionItem.click((event) => this._handleFilterClick(event));
            $(this.el).find('#filter-menu ul').append($collectionItem);
            $(this.el).find('#filter-inputs').append($formInput);
        }

        // Setup datetimepickers.
        for (index in this._datetimepickerElements)
        {
            var elementId = this._datetimepickerElements[index];
            $(this.el).find(elementId).datetimepicker();
            $(this.el).find(elementId).data('DateTimePicker').format(Configuration.DATETIME_FORMAT);
            $(this.el).find(elementId).on('dp.change', () => this._handleSearch());
        }

        $(this.el).find('#filter-inputs input').on('change keyup paste mouseup', () => this._handleSearch());
        $(this.el).find('#filter-inputs select').on('change keyup paste mouseup', () => this._handleSearch());

        this._filtersInjected = true;
        this._hideFormElements();
    }

    /**
     * Get text filter.
     */
    _getFilterText(label, field)
    {
        var templateChoice = _.template($(this.options.templateFilterChoice).html());
        var templateInput = _.template($(this.options.templateFilterText).html());
        var htmlChoice = templateChoice({label: label, field: field});
        var htmlInput = templateInput({label: label, field: field});
        return {collectionItem: htmlChoice, input: htmlInput};
    }

    /**
     * Get master datetime filter template.
     */
    _getFilterDatetime(label, field)
    {
        var templateChoice = _.template($(this.options.templateFilterChoice).html());
        var templateInput = _.template($(this.options.templateFilterDatetime).html());
        var htmlChoice = templateChoice({label: label, field: field});
        var htmlInput = templateInput({label: label, field: field});
        return {collectionItem: htmlChoice, input: htmlInput};
    }

    /**
     * Get the filter for resource labels
     */
    _getFilterLabels(label, field)
    {
        var templateChoice = _.template($(this.options.templateFilterChoice).html());
        var templateInput = _.template($(this.options.templateFilterMultipleEnum).html());
        var labelCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABEL_COLLECTION);
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        var project_resources = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCES_CURRENT, {data: {project: project.id}});
        var labels = new Set();
        project_resources.each(function (resource) {
            resource.attributes.labels.forEach(function (url) {
                labels.add(url);
            });
        });
        var filtered_collection = labelCollection.filter(function (resource) { return labels.has(resource.attributes.url); });
        var labelModels = filtered_collection.map((label) => {
            return {
                label: label.get('name'),
                value: label.get('uuid')
            };
        });
        var htmlChoice = templateChoice({label: label, field: field});
        var htmlInput = templateInput({label: label, field: field, values: labelModels});
        return {collectionItem: htmlChoice, input: htmlInput};
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Event handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles filter click.
     */
    _handleFilterClick(event)
    {
        var data = $(event.target).data();
        //this._hideFormElements();
        if (data.id)
        {
            this._showFormElement(data.id);
        }
    }

    /**
     * Handle search.
     */
    _handleSearch()
    {
        // Only use this if the collection has a URL.
        if (!this.view.collection.route)
        {
            return;
        }

        var values = $(this.el).find('form').serializeArray();
        var filters = {};
        for (var index in values)
        {
            var name = values[index].name;
            var value = values[index].value;
            if (typeof filters[name] === 'undefined') {
                filters[name] = value;
            } else if (typeof filters[name] === 'string') {
                filters[name] = [filters[name], value];
            } else {
                filters[name].push(value);
            }
        }
        this.view.collection.fetchFilter(filters);
    }

    /**
     * Handles sort request.
     *
     * Defaults to ascending. Only goes descending if the associated ascending
     * CSS style is currently attached to the target th.
     */
    _handleSort(event)
    {
        // Only use this if the collection has a route.
        if (!this.view.collection.route)
        {
            return;
        }

        var sortField = $(event.currentTarget).attr('data-name');
        if (sortField)
        {
            // Check for sort arrow "up" already there. If so, we want down (else, up).
            var ascending = true;
            if ($(event.currentTarget).find('span.glyphicon-arrow-up').length > 0)
            {
                ascending = false;
            }

            // Do the sort.
            this.view.collection.fetchSort(ascending, sortField);

            // Set the sort arrows properly.
            $(event.currentTarget).parent().find('th span.glyphicon').remove();
            if (ascending)
            {
                $(event.currentTarget).append('<span class="glyphicon glyphicon-arrow-up"></span>');
            }
            else
            {
                $(event.currentTarget).append('<span class="glyphicon glyphicon-arrow-down"></span>');
            }
        }
    }

    /**
     * Handle pagination previous.
     */
    _handlePaginationPrevious()
    {
        var pagination = this.view.collection.getPagination();
        var data = this._getURLQueryParameters(pagination.get('previous'));
        if (data.page)
        {
            this.view.collection.fetchPage({page: data.page});
        }
        else
        {
            this.view.collection.fetchPage({});
        }
    }

    /**
     * Handle pagination next.
     */
    _handlePaginationNext()
    {
        var pagination = this.view.collection.getPagination();
        var data = this._getURLQueryParameters(pagination.get('next'));
        this.view.collection.fetchPage({page: data.page});
    }

    /**
     * Handle pagination first.
     */
    _handlePaginationFirst()
    {
        this.view.collection.fetchPage({page: 1});
    }

    /**
     * Handle pagination last.
     */
    _handlePaginationLast()
    {
        var pagination = this.view.collection.getPagination();
        this.view.collection.fetchPage({page: pagination.get('total')});
    }

    /**
     * Handles collection event.
     */
    _handleCollectionEventSync(collection)
    {
        if (collection instanceof BaseCollection)
        {
            // We only inject if: the table exists, a route exists, we haven't injected yet, and the table has items.
            if ($(this.el).find(this.options.table).length > 0 &&
                collection.route &&
                !this._filtersInjected &&
                collection.length > 0)
            {
                var options = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE_OPTIONS, {route: collection.route});
                if (options)
                {
                    this._injectFiltering(options.filter_fields);
                }
            }

            // Handle pagination.
            this._processPagination(collection);
        }
    }

    /**
     * Handle button remove.
     */
    _handleButtonRemove(event)
    {
        var data = $(event.target).data();
        this._hideFormElement(data.id);
        this._handleSearch();
    }

    /**
     * Handle button clear all.
     */
    _handleButtonClearAll(event)
    {
        var data = $(event.target).data();
        this._hideFormElements();
        this._handleSearch();
    }

    /**
     * Handle row left click.
     */
    _handleLeftClickRow(event)
    {
        if (this.view.allowMultipleSelection)
        {
            // Wipe everything if ctrl key not selected.
            if (!event[this._multipleSelectionKey])
            {
                $(event.currentTarget).addClass('active clickable-row').siblings().removeClass('active');
            }
            else
            {
                $(event.currentTarget).toggleClass('active');
            }

            // If shift down, select range.
            if (event[this._rangeSelectionKey])
            {
                $(this._lastTarget).addClass('active clickable-row')
                if ($(this._lastTarget).index() <= $(event.currentTarget).index())
                {
                    $(this._lastTarget).nextUntil(event.currentTarget).addClass('active clickable-row');
                }
                else
                {
                    $(event.currentTarget).nextUntil(this._lastTarget).addClass('active clickable-row');
                }
            }
            else
            {
                this._lastTarget = event.currentTarget;
            }
        }
        else
        {
            $(event.currentTarget).addClass('active clickable-row').siblings().removeClass('active');
            this._lastTarget = event.currentTarget;
        }
    }

    /**
     * Handles right click on row.
     */
    _handleRowRightClick(event)
    {
        if (this.view.contextMenu)
        {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__CONTEXTMENU_SHOW, {top: event.pageY,
                                                                                    left: event.pageX,
                                                                                    items: this.view.contextMenu});
        }
        return false;
    }

    /**
     * Handle pagination change.
     */
    _handlePaginationSelect(event)
    {
        this.view.collection.fetchPage({page: parseInt(event.currentTarget.value)});
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns query parameters from passed URL string.
     *
     * TODO: move this out of here...
     */
    _getURLQueryParameters(string)
    {
        var queryString = string.substr(string.indexOf('?') + 1),
            match,
            pl     = /\+/g,  // Regex for replacing addition symbol with a space
            search = /([^&=]+)=?([^&]*)/g,
            decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); };

        var urlParams = {};
        while (match = search.exec(queryString))
            urlParams[decode(match[1])] = decode(match[2]);
        return urlParams;
    }

    /**
     * Hide all form elements for the table control.
     */
    _hideFormElements()
    {
        $(this.el).find('#filter-inputs div input').val('');
        $(this.el).find('#filter-inputs div select').val('');
        $(this.el).find('#filter-inputs').children().hide();
    }

    /**
     * Hide form element of given ID.
     */
    _hideFormElement(elementId)
    {
        $(this.el).find('#filter-inputs div#' + elementId + ' input').val('');
        $(this.el).find('#filter-inputs div#' + elementId + ' select').val('');
        $(this.el).find('#filter-inputs div#' + elementId).hide();
    }

    /**
     * Shows form element of given ID.
     */
    _showFormElement(elementId)
    {
        $(this.el).find('#filter-inputs div#' + elementId).show();
    }

    /**
     * Process pagination.
     */
    _processPagination(collection)
    {
        // Initialize pagination controls.
        $(this.el).find('.table-control #pagination-first').prop('disabled', true);
        $(this.el).find('.table-control #pagination-previous').prop('disabled', true);
        $(this.el).find('.table-control #pagination-next').prop('disabled', true);
        $(this.el).find('.table-control #pagination-last').prop('disabled', true);

        $(this.el).find('.table-control #pagination-first').hide();
        $(this.el).find('.table-control #pagination-previous').hide();
        $(this.el).find('.table-control #pagination-next').hide();
        $(this.el).find('.table-control #pagination-last').hide();

        $(this.el).find('.table-control #pagination-select').hide();
        $(this.el).find('.table-control #pagination-select').empty();
        $(this.el).find('.table-control #pagination-select-text').hide();
        Radio.channel('radio').request(RODAN_EVENTS.REQUEST__UPDATE_NAVIGATION_PAGINATION);

        // If collection, setup pagination.
        if (collection)
        {
            var pagination = collection.getPagination();
            if (pagination !== null)
            {
                // Handle select and show buttons
                if (pagination.get('total') > 1)
                {
                    var select = $(this.el).find('.table-control #pagination-select');
                    select.prop('disabled', false);
                    for (var i = 1; i <= pagination.get('total'); i++)
                    {
                        select.append($('<option>', {value: i, text: i}));
                    }
                    select.val(pagination.get('current'));
                    $(this.el).find('.table-control #pagination-first').show();
                    $(this.el).find('.table-control #pagination-previous').show();
                    $(this.el).find('.table-control #pagination-next').show();
                    $(this.el).find('.table-control #pagination-last').show();
                    $(this.el).find('.table-control #pagination-select').show();
                }

                // Setup buttons.
                if (pagination.get('current') > 1)
                {
                    $(this.el).find('.table-control div#pagination').show();
                    $(this.el).find('.table-control #pagination-first').prop('disabled', false);
                    $(this.el).find('.table-control #pagination-previous').prop('disabled', false);
                }
                if (pagination.get('current') < pagination.get('total'))
                {
                    $(this.el).find('.table-control div#pagination').show();
                    $(this.el).find('.table-control #pagination-next').prop('disabled', false);
                    $(this.el).find('.table-control #pagination-last').prop('disabled', false);
                }

            }
        }
    }
}

///////////////////////////////////////////////////////////////////////////////////////
// PROTOTYPE
///////////////////////////////////////////////////////////////////////////////////////
BehaviorTable.prototype.ui = {
    paginationPrevious: '#pagination-previous',
    paginationNext: '#pagination-next',
    paginationFirst: '#pagination-first',
    paginationLast: '#pagination-last',
    buttonSearch: '#button-search',
    buttonRemove: '#button-remove',
    buttonClearAll: '#button-clearall',
    paginationSelect: '#pagination-select'
};
BehaviorTable.prototype.events = {
    'click @ui.paginationPrevious': '_handlePaginationPrevious',
    'click @ui.paginationNext': '_handlePaginationNext',
    'click @ui.paginationFirst': '_handlePaginationFirst',
    'click @ui.paginationLast': '_handlePaginationLast',
    'click th': '_handleSort',
    'click @ui.buttonSearch': '_handleSearch',
    'click @ui.buttonRemove': '_handleButtonRemove',
    'click @ui.buttonClearAll': '_handleButtonClearAll',
    'click tbody tr': '_handleLeftClickRow',
    'contextmenu tbody tr': '_handleRowRightClick',
    'change @ui.paginationSelect': '_handlePaginationSelect'
};
BehaviorTable.prototype.options = {
    'templateControl': '#template-table_control',
    'templateFilterChoice': '#template-filter_choice',
    'templateFilterText': '#template-filter_text',
    'templateFilterEnum': '#template-filter_enumeration',
    'templateFilterDatetime': '#template-filter_datetime',
    'templateFilterMultipleEnum': '#template-filter_multiple_enum',
    'table': 'table'
};
BehaviorTable.prototype.collectionEvents = {
    'sync': '_handleCollectionEventSync'
};
