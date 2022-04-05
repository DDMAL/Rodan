import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';

/**
 * This is a layout to help render a Collection and a single item.
 * We're using a LayoutView as opposed to a CompositeView because the single model
 * that would be associated with the CompositveView is not initially known, so it can't
 * rerender.
 */
export default class LayoutViewModel extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this.addRegions({
            regionCollection: '#region-main_layoutview_model_collection',
            regionItem: '#region-main_layoutview_model_item'
        });
    }

    /**
     * Show a Collection view.
     *
     * @param {Marionette.View} view Collection view to show
     */
    showCollection(view)
    {
        this.showChildView('regionCollection', view);
    }

    /**
     * Show an item view.
     *
     * @param {Marionette.View} view item view to show
     */
    showItem(view)
    {
        this.showChildView('regionItem', view);
    }

    /**
     * Clears item view.
     */
    clearItemView()
    {
        this.getRegion('regionItem').empty();
    }
}
LayoutViewModel.prototype.template = _.template($('#template-main_layoutview_model').text());
