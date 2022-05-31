import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * RunJob view.
 */
export default class ViewRunJob extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Set 'Open' button availability after render.
     *
     * @todo this is a hack to make sure the client shows what runjobs are manual and available
     */
    onRender()
    {
    	$(this.el).find('#button-open_runjob').prop('disabled', !this.model.available());
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle double-click.
     */
    _handleButtonOpen()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RUNJOB_ACQUIRE, {runjob: this.model});
    }
}
ViewRunJob.prototype.modelEvents = {
    'all': 'render'
};
ViewRunJob.prototype.ui = {
    buttonOpen: '#button-open_runjob'
};
ViewRunJob.prototype.events = {
    'click @ui.buttonOpen': '_handleButtonOpen'
        };
ViewRunJob.prototype.template = _.template($('#template-main_runjob_individual').text());
