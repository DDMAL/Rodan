import $ from 'jquery';
import _ from 'underscore';
import LayoutViewMain from './Main/LayoutViewMain';
import LayoutViewNavigation from './Navigation/LayoutViewNavigation';
import LayoutViewStatus from './Status/LayoutViewStatus';
import Marionette from 'backbone.marionette';

/**
 * Layout view for master work area.
 */
export default class LayoutViewMaster extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the view.
     */
    initialize()
    {
        this.addRegions({
            regionMain: '#region-main',
            regionNavigation: '#region-navigation',
            regionStatus: '#region-status'
        });
        this._initializeViews();

    }

    /**
     * Shows the main and navigation views.
     */
    onRender()
    {
        this.showChildView('regionMain', this._layoutViewMain);
        this.showChildView('regionNavigation', this._layoutViewNavigation);
        this.showChildView('regionStatus', this._layoutViewStatus);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize all the views so they can respond to events.
     */
    _initializeViews()
    {
        this._layoutViewNavigation = new LayoutViewNavigation();
        this._layoutViewMain = new LayoutViewMain();
        this._layoutViewStatus = new LayoutViewStatus();
    }
}
LayoutViewMaster.prototype.template = _.template($('#template-master').text());
