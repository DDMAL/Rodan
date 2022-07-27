import $ from 'jquery';
import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Controls context menus.
 */
export default class ControllerContextMenu extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__CONTEXTMENU_HIDE, () => this._handleRequestContextMenuHide());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__CONTEXTMENU_SHOW, options => this._handleRequestContextMenuShow(options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle request context menu hide.
     */
    _handleRequestContextMenuHide()
    {
        $('#menu-context').hide();
    }

    /**
     * Handle request context menu show.
     */
    _handleRequestContextMenuShow(options)
    {
        $('#menu-context').empty();
        for (var index in options.items)
        {
            var itemData = options.items[index];
            var callOptions = itemData.options ? itemData.options : {};
            var label = itemData.label;
            var channel = itemData.channel ? itemData.channel : 'rodan';
            var radiorequest = itemData.radiorequest;

            var functionCall = (event) => {
                var data = $(event.currentTarget).data('radio');
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__CONTEXTMENU_HIDE);
                Radio.channel(channel).request(data.request, data.options);
            };

            var anchor = $('<a>' + label + '</a>');
            anchor.data('radio', {request: radiorequest, options: callOptions});
            anchor.click(functionCall);
            $('#menu-context').append($('<li></li>').append(anchor));
        }
        $('#menu-context').css('top', options.top);
        $('#menu-context').css('left', options.left);
        $('#menu-context').show();
        $('body').one('click', this._handleRequestContextMenuHide);
    }
}