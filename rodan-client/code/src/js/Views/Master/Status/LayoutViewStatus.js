import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * Status view.
 */
export default class LayoutViewStatus extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the view.
     */
    initialize()
    {
        /** @ignore */
        this._pending = 0;
        /** @ignore */
        this._completed = 0;

        this._updateStatusBar();
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__SERVER_REQUESTS_PENDING_UPDATE, (options) => this._handleEventPendingRequests(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__SERVER_IDLE, () => this._handleEventServerNotice('progress-bar'));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__SERVER_WAIT, () => this._handleEventServerNotice('progress-bar-warning'));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__SERVER_PANIC, () => this._handleEventServerNotice('progress-bar-danger'));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle pending requests event.
     */
    _handleEventPendingRequests(options)
    {
        if (options.pending > this._pending)
        {
            this._pending = options.pending;
        }
        else if (options.pending > 0)
        {
            if (this._pending - options.pending > this._completed)
            {
                this._completed = this._pending - options.pending;
            }
            else
            {
                this._pending = options.pending + this._completed;
            }
        }
        else
        {
            this._pending = 0;
            this._completed = 0;
        }
        this._updateStatusBar();
    }

    /**
     * Handle event server notice.
     */
    _handleEventServerNotice(cssClass)
    {
        $(this.el).find('div#statusbar').removeClass();
        $(this.el).find('div#statusbar').addClass(cssClass);
    }

    /**
     * Sets status bar.
     */
    _updateStatusBar()
    {
        var text = '' + this._completed + ' of ' + this._pending + ' requests pending...';
        var percent = 100;
        if (this._completed === this._pending)
        {
            var text = 'No pending requests';
        }
        else
        {
            percent = Math.floor(this._completed * 100 / this._pending);
        }
        $(this.el).find('div#statusbar').width(percent + '%');
        $(this.el).find('#status-pending_responses').text(text);
    }
}
LayoutViewStatus.prototype.template = _.template($('#template-status').text());
