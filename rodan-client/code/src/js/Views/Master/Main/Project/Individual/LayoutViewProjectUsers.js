import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * Project admin view.
 */
export default class LayoutViewProjectUsers extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.viewusers', 'options.viewprojectadmins' and 'options.viewprojectworkers' must be provided (each being Marionette.Views); also required is 'options.project' (Project)
     */
    initialize(options)
    {
        this.addRegions({
            regionProjectAdmins: '#region-main_projectusers_admins',
            regionProjectWorkers: '#region-main_projectusers_workers',
            regionUsers: '#region-main_projectusers_users'
        });
        this._viewProjectAdmins = options.viewprojectadmins;
        this._viewProjectWorkers = options.viewprojectworkers;
        this._viewUsers = options.viewusers;
        this._project = options.project;
    }

    /**
     * Unbind from events.
     */
    onDestroy()
    {
        Radio.channel('rodan').off(null, null, this);
        Radio.channel('rodan').stopReplying(null, null, this);
    }

    /**
     * Before the view shows we make sure the subviews are shown.
     */
    onRender()
    {
        this.showChildView('regionProjectAdmins', this._viewProjectAdmins);
        this.showChildView('regionProjectWorkers', this._viewProjectWorkers);
        this.showChildView('regionUsers', this._viewUsers);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button add admin.
     */
    _handleButtonAddAdmin()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_ADD_USER_ADMIN,
                                       {username: this._getSelectedUser(), project: this._project});
    }

    /**
     * Handle button add worker.
     */
    _handleButtonAddWorker()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_ADD_USER_WORKER,
                                       {username: this._getSelectedUser(), project: this._project});
    }

    /**
     * Get currently selected user.
     */
    _getSelectedUser()
    {
        return $('#region-main_projectusers_users select').find(":selected").text().trim();
    }
}
LayoutViewProjectUsers.prototype.template = _.template($('#template-main_project_users').text());
LayoutViewProjectUsers.prototype.ui = {
    buttonAddAdmin: '#button-projectusers_add_admin',
    buttonAddWorker: '#button-projectusers_add_worker'
};
LayoutViewProjectUsers.prototype.events = {
    'click @ui.buttonAddAdmin': '_handleButtonAddAdmin',
    'click @ui.buttonAddWorker': '_handleButtonAddWorker'
};
