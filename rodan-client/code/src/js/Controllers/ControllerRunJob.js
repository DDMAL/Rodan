import $ from 'jquery';
import _ from 'underscore';
import BaseController from './BaseController';
import Configuration from 'js/Configuration';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import LayoutViewModel from 'js/Views/Master/Main/LayoutViewModel';
import Radio from 'backbone.radio';
import RunJobCollection from 'js/Collections/RunJobCollection';
import ViewRunJob from 'js/Views/Master/Main/RunJob/Individual/ViewRunJob';
import ViewRunJobCollection from 'js/Views/Master/Main/RunJob/Collection/ViewRunJobCollection';
import ViewRunJobCollectionItem from 'js/Views/Master/Main/RunJob/Collection/ViewRunJobCollectionItem';

/**
 * Controller for RunJobs.
 */
export default class ControllerRunJob extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this._runJobLocks = {};
 //       setInterval(() => this._reacquire(), Configuration.RUNJOB_ACQUIRE_INTERVAL);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RUNJOB_SHOWLAYOUTVIEW, options => this._handleCommandShowLayoutView(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RUNJOB_SELECTED, options => this._handleEventItemSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RUNJOB_SELECTED_COLLECTION, options => this._handleEventCollectionSelected(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RUNJOB_ACQUIRE, options => this._handleRequestAcquire(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RUNJOBS_LOAD, options => this._handleRequestRunJobs(options));
    }

    /**
     * Handle show LayoutView.
     */
    _handleCommandShowLayoutView(options)
    {
        this._layoutView = options.layoutView;
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options)
    {
        this._layoutView.showItem(new ViewRunJob({model: options.runjob}));
    }

    /**
     * Handle event collection selected.
     */
    _handleEventCollectionSelected(options)
    {
        this._collection = new RunJobCollection();
        this._collection.fetch({data: {project: options.project.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [this._collection]});
        this._layoutView = new LayoutViewModel();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: this._layoutView});
        var view = new ViewRunJobCollection({collection: this._collection,
                                       template: _.template($('#template-main_runjob_collection').text()),
                                       childView: ViewRunJobCollectionItem});
        this._layoutView.showCollection(view);
    }

    /**
     * Handle request acquire.
     */
    _handleRequestAcquire(options)
    {
        // Get lock if available. Else, if we already have the lock, simply open the interface.
        var user = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_USER);
        var runJobUrl = options.runjob.get('url');
        if (options.runjob.available())
        {
            var ajaxSettings = {
                url: options.runjob.get('interactive_acquire'),
                type: 'POST',
                dataType: 'json',
                success: (response) => this._handleSuccessAcquire(response, runJobUrl, options.runjob),
                error: () => this._removeRunJobLock(runJobUrl)
            };
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
        }
        else if (options.runjob.get('working_user') === user.get('url'))
        {
            var url = this._getWorkingUrl(runJobUrl);
            this._openRunJobInterface(url);
        }
    }

    /**
     * Handle success of interactive acquire.
     */
    _handleSuccessAcquire(response, runJobUrl, runJob)
    {
//        this._registerRunJobForReacquire(runJobUrl, response.working_url, runJob.get('interactive_acquire'));
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_ACQUIRED, {runjob: runJob});
        this._openRunJobInterface(response.working_url);
    }

    /**
     * Opens interface.
     */
    _openRunJobInterface(url)
    {
        window.open(url, '', '_blank');
    }

    /**
     * Registers an interactive job to be relocked.
     */
    _registerRunJobForReacquire(runJobUrl, workingUrl, acquireUrl)
    {
        var date = new Date();
        this._runJobLocks[runJobUrl] = {date: date.getTime(), working_url: workingUrl, acquire_url: acquireUrl};
    }

    /**
     * Get working URL for acquired RunJob.
     */
    _getWorkingUrl(runJobUrl)
    {
        var object = this._runJobLocks[runJobUrl];
        if (object)
        {
            return object.working_url;
        }
        return null;
    }

    /**
     * Handle reacquire callback.
     */
    _reacquire()
    {
        var date = new Date();
        for (var runJobUrl in this._runJobLocks)
        {
            var runJob = this._collection.findWhere({url: runJobUrl});

            // If the RunJob is available, renew. Else, get rid of the lock.
            if (runJob.available())
            {
                var data = this._runJobLocks[runJobUrl];
                if (data)
                {
                    var timeElapsed = date.getTime() - data.date;
                    if (timeElapsed < Configuration.RUNJOB_ACQUIRE_DURATION)
                    {
                        $.ajax({url: data.acquire_url, type: 'POST', dataType: 'json', error: () => this._removeRunJobLock(runJobUrl)});
                    }
                    else
                    {
                        this._removeRunJobLock(runJobUrl);
                    }
                }
            }
            else
            {
                this._removeRunJobLock(runJobUrl);
            }
        }
    }

    /**
     * Remove RunJob lock.
     */
    _removeRunJobLock(runJobUrl)
    {
        this._runJobLocks[runJobUrl] = null;
    }

    /**
     * Handle request RunJobs.
     */
    _handleRequestRunJobs(options)
    {
        this._collection = new RunJobCollection();
        this._collection.fetch(options);
        return this._collection;
    }
}
