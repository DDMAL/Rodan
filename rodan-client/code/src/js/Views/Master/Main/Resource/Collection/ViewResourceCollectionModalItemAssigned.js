import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Resource item View for Collection in modal to display assigned resources.
 */
export default class ViewResourceCollectionModalItemAssigned extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; options.requestdata (object; data sent with requests), options.unassignrequest (object; when item becomes unassigned, this request is sent), options.moveup (object; when item is to be moved up, this request is sent), options.movedown (object; when item is to be moved down, this request is sent)
     */
    initialize(options)
    {
        this._requestData = options.requestdata;
        this._unassignRequest = options.unassignrequest;
        this._moveUp = options.moveup;
        this._moveDown = options.movedown;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    _handleDoubleClick()
    {
        this._requestData.resource = this.model;
        Radio.channel('rodan').request(this._unassignRequest, this._requestData);
    }

    _handleMoveUp()
    {
        this._requestData.resource = this.model;
        Radio.channel('rodan').request(this._moveUp, this._requestData);
    }

    _handleMoveDown()
    {
        this._requestData.resource = this.model;
        Radio.channel('rodan').request(this._moveDown, this._requestData);
    }
}
ViewResourceCollectionModalItemAssigned.prototype.template = _.template($('#template-modal_resource_collection_item_assigned').text());
ViewResourceCollectionModalItemAssigned.prototype.tagName = 'tr';
ViewResourceCollectionModalItemAssigned.prototype.ui = {
    moveUp: '.move-up',
    moveDown: '.move-down',
};
ViewResourceCollectionModalItemAssigned.prototype.events = {
    'dblclick': '_handleDoubleClick',
    'click @ui.moveUp': '_handleMoveUp',
    'click @ui.moveDown': '_handleMoveDown',
};
