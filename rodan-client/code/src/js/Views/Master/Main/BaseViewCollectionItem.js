import Marionette from 'backbone.marionette';

/**
 * Base Collection Item view.
 */
export default class BaseViewCollectionItem extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Set description after render.
     */
    onRender()
    {
        var description = 'no description available';
        if (this.model.has('description') && this.model.get('description') !== '')
        {
            description = this.model.get('description');
        }
        this.$el.attr('title', description);
    }
}
BaseViewCollectionItem.prototype.tagName = 'tr';
BaseViewCollectionItem.prototype.modelEvents = {
    'change': 'render'
};
