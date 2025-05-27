import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * RunJob Collection item view.
 */
export default class ViewRunJobCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Set availability  property before render.
     *
     * @todo this is a hack to make sure the client shows what runjobs are manual and available
     */
    onBeforeRender()
    {
        this.model.set('available', this.model.available());
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles click.
     */
    _handleClick()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_SELECTED, {runjob: this.model});
    }
}
ViewRunJobCollectionItem.prototype.template = _.template($('#template-main_runjob_collection_item').text());
ViewRunJobCollectionItem.prototype.tagName = 'tr';
ViewRunJobCollectionItem.prototype.events = {
    'click': '_handleClick'
};
