import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import NAV_EVENTS from './Events';
import Radio from 'backbone.radio';

/**
 * This class represents a navigation menu node.
 */
export default class ViewNavigationNode extends Marionette.CollectionView
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     */
    initialize()
    {
        Radio.channel('rodan-navigation').on(NAV_EVENTS.EVENT__NAVIGATION_SELECTED_NODE, event => this._handleEventNodeSelected(event));
    }

    /**
     * Hide subviews on render (initially).
     */
    onRender()
    {
        this._hideSubviews();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Sets highlight of this menu entry.
     */
    _setHighlight(highlight)
    {
        var node = $(this.$el.find('.node_text')[0]);
        if (highlight)
        {
            // TODO magic number
            node.css('background-color', '#444444');
        }
        else
        {
            node.css('background-color', '');
        }
    }

    /**
     * Handle click.
     */
    _handleClick(event)
    {
        this._toggleSubviews();
        event.stopPropagation();
        this._sendClickEvents();
    }

    /**
     * Toggle subview show.
     */
    _toggleSubviews()
    {
        var firstUl = $(this.$el.find(this.childViewContainer)[0]);
        if (firstUl !== undefined && firstUl.find('div').length > 0)
        {
            firstUl.toggle('fast');
        }
    }

    /**
     * Hide subvies.
     */
    _hideSubviews()
    {
        var firstUl = $(this.$el.find(this.childViewContainer)[0]);
        if (firstUl !== undefined)
        {
            firstUl.hide();
        }
    }

    /**
     * Show subviews.
     */
    _showSubviews()
    {
        // Show subviews.
        var firstUl = $(this.$el.find(this.childViewContainer)[0]);
        if (firstUl !== undefined)
        {
            firstUl.show();
        }
    }

    /**
     * Expand parent.
     */
     _expandParent()
     {
        // Show parents.
        if (this._parent !== null && this._parent !== undefined && this._parent instanceof ViewNavigationNode)
        {
            this._parent._showSubviews();
            this._parent._expandParent();
        }
    }

    /**
     * Does highlighting.
     */
    _handleEventNodeSelected(event)
    {
        if (this === event.node)
        {
            this._setHighlight(true);
            this._expandParent();
        }
        else
        {
            this._setHighlight(false);
        }
    }
}
ViewNavigationNode.prototype.ui = {
    text: '.node_text'
};
ViewNavigationNode.prototype.events = {
    'click @ui.text': '_handleClick'
};
ViewNavigationNode.prototype.template = _.template($('#template-navigation_node').text());
ViewNavigationNode.prototype.childViewContainer = 'ul';
