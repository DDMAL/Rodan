import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Resource item View for Collection in modal.
 */
export default class ViewResourceCollectionModalItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.assigned' (boolean; true if this item belongs to the "assigned" Collection), options.requestdata (object; data sent with requests), options.assignrequest (object; when item becomes assigned, this request is sent), options.unassignrequest (object; when item becomes unassigned, this request is sent)
     */
    initialize(options)
    {
        this._assigned = options.assigned;
        this._requestData = options.requestdata;
        this._assignRequest = options.assignrequest;
        this._unassignRequest = options.unassignrequest;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles double click.
     */
    _handleDoubleClick()
    {
        this._requestData.resource = this.model;
        if (this._assigned)
        {
            Radio.channel('rodan').request(this._unassignRequest, this._requestData); 
        }
        else
        {
            Radio.channel('rodan').request(this._assignRequest, this._requestData); 
        }
    }
}
ViewResourceCollectionModalItem.prototype.template = _.template($('#template-modal_resource_collection_item').text());
ViewResourceCollectionModalItem.prototype.tagName = 'tr';
ViewResourceCollectionModalItem.prototype.events = {'dblclick': '_handleDoubleClick'};
