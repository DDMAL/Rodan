import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';

/**
 * ResourceType view.
 */
export default class ViewResourceTypeCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * After render, set the value of the 'option.value'.
     */
    onRender()
    {
        super.onRender();
        this.$el.attr('value', this.model.get('url'));
        if (this.model.has('selected'))
        {
            this.$el.attr('selected', 'selected');
        }
    }
}
ViewResourceTypeCollectionItem.prototype.template = _.template($('#template-resourcetype_collection_item').text());
ViewResourceTypeCollectionItem.prototype.tagName = 'option';
