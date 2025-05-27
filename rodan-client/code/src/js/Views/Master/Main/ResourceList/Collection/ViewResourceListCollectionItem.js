import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Item view for ResourceList Collection.
 */
export default class ViewResourceListCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles click.
     */
    _handleClick()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED, {resourcelist: this.model});
    }

    /**
     * Handles double click.
     */
    _handleDblClick()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_DOWNLOAD, {resourcelist: this.model});
    }
}
ViewResourceListCollectionItem.prototype.template = _.template($('#template-main_resourcelist_collection_item').text());
ViewResourceListCollectionItem.prototype.tagName = 'tr';
ViewResourceListCollectionItem.prototype.events = {
    'click': '_handleClick',
    'dblclick': '_handleDblClick'
};
