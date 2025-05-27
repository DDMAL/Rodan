import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import Utilities from 'js/Shared/Utilities';

/**
 * ResourceType detail view.
 */
export default class ViewResourceTypeDetailCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles button.
     */
    _handleButton()
    {
        Utilities.copyTextToClipboard(this.model.get('url'));
    }
}
ViewResourceTypeDetailCollectionItem.prototype.template = _.template($('#template-resourcetype_detail_collection_item').text());
ViewResourceTypeDetailCollectionItem.prototype.tagName = 'tr';
ViewResourceTypeDetailCollectionItem.prototype.events = {
    'click @ui.button': '_handleButton'
};
ViewResourceTypeDetailCollectionItem.prototype.ui = {
    'button': '#button-copy_url'
};
