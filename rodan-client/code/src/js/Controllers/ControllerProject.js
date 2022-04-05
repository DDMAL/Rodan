import $ from 'jquery';
import _ from 'underscore';
import BaseController from './BaseController';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import LayoutViewModel from 'js/Views/Master/Main/LayoutViewModel';
import LayoutViewProjectUsers from 'js/Views/Master/Main/Project/Individual/LayoutViewProjectUsers';
import Project from 'js/Models/Project';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import UserCollection from 'js/Collections/UserCollection';
import ViewProject from 'js/Views/Master/Main/Project/Individual/ViewProject';
import ViewProjectCollection from 'js/Views/Master/Main/Project/Collection/ViewProjectCollection';
import ViewUserCollectionItem from 'js/Views/Master/Main/User/Collection/ViewUserCollectionItem';
import ViewWorkflowRunCollection from 'js/Views/Master/Main/WorkflowRun/Collection/ViewWorkflowRunCollection';
import WorkflowRunCollection from 'js/Collections/WorkflowRunCollection';

/**
 * Controller for Projects.
 */
export default class ControllerProject extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize the instance.
     */
    initialize()
    {
        this._activeProject = null;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - initialization
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        // Events.
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_ADDED_USER_ADMIN, options => this._handleEventProjectAddedUserAdmin(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_ADDED_USER_WORKER, options => this._handleEventProjectAddedUserWorker(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_CREATED, options => this._handleEventProjectGenericResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_DELETED, options => this._handleEventProjectDeleteResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_REMOVED_USER_ADMIN, options => this._handleEventProjectRemovedUser(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_REMOVED_USER_WORKER, options => this._handleEventProjectRemovedUser(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_SAVED, options => this._handleEventProjectGenericResponse(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_SELECTED, options => this._handleEventItemSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_SELECTED_COLLECTION, () => this._handleEventCollectionSelected());
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, options => this._handleEventProjectShowUsers(options));

        // Requests.
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_ADD_USER_ADMIN, (options) => this._handleRequestProjectAddUserAdmin(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_ADD_USER_WORKER, (options) => this._handleRequestProjectAddUserWorker(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE, () => this._handleRequestProjectActive());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_CREATE, options => this._handleRequestCreateProject(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_SET_ACTIVE, options => this._handleRequestSetActiveProject(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_SAVE, options => this._handleRequestProjectSave(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_DELETE, options => this._handleRequestProjectDelete(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_REMOVE_USER_ADMIN, options => this._handleRequestRemoveUserAdmin(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__PROJECT_REMOVE_USER_WORKER, options => this._handleRequestRemoveUserWorker(options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Event handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event Project show users.
     */
    _handleEventProjectShowUsers(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);

        // Make sure project is updated.
        options.project.fetch();

        // Create collections to store admins and workers.
        var adminUserCollection = new UserCollection();
        var workerUserCollection = new UserCollection();

        // Get admins and workers for project.
        var ajaxSettingsAdmins = {success: (response) => this._handleProjectGetAdminsSuccess(response, adminUserCollection),
                                  error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                                  type: 'GET',
                                  dataType: 'json',
                                  url: options.project.get('url') + 'admins/'};
        var ajaxSettingsWorkers = {success: (response) => this._handleProjectGetWorkersSuccess(response, workerUserCollection),
                                   error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                                   type: 'GET',
                                   dataType: 'json',
                                   url: options.project.get('url') + 'workers/'};
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettingsAdmins});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettingsWorkers});

        // Need collection for all users.
        var collection = new UserCollection();
        collection.fetch();
        var userSelectionView = new BaseViewCollection({collection: collection,
                                                        template: _.template($('#template-main_user_selection').text()),
                                                        childView: BaseViewCollectionItem,
                                                        childViewContainer: 'select',
                                                        childViewOptions: {template: _.template($('#template-main_user_selection_item').text()),
                                                                           tagName: 'option'}});

        // Create view.
        var projectAdminsView = new BaseViewCollection({collection: adminUserCollection,
                                                        template: _.template($('#template-main_user_collection').text()),
                                                        childView: ViewUserCollectionItem,
                                                        childViewOptions: {template: _.template($('#template-main_user_collection_item_remove').text()),
                                                                           project: options.project,
                                                                           admin: true}});
        var projectWorkersView = new BaseViewCollection({collection: workerUserCollection,
                                                         template: _.template($('#template-main_user_collection').text()),
                                                         childView: ViewUserCollectionItem,
                                                         childViewOptions: {template: _.template($('#template-main_user_collection_item_remove').text()),
                                                                            project: options.project}});
        var view = new LayoutViewProjectUsers({viewusers: userSelectionView,
                                               viewprojectadmins: projectAdminsView,
                                               viewprojectworkers: projectWorkersView,
                                               project: options.project});

        // Show modal.
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {content: view, title: 'Project Users'});
    }

    /**
     * Handle event Project generic response.
     */
    _handleEventProjectGenericResponse()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_PROJECTS_LOAD, {});
    }

    /**
     * Handle event Project delete response.
     */
    _handleEventProjectDeleteResponse()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_PROJECTS_LOAD, {});
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_SELECTED_COLLECTION);
    }

    /**
     * Handle request Project save.
     */
    _handleRequestProjectSave(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Saving Project', content: 'Please wait...'});
        options.project.save(options.fields, {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_SAVED, {project: model})});
    }

    /**
     * Handle request Project create.
     */
    _handleRequestCreateProject(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Creating Project', content: 'Please wait...'});
        var project = new Project({creator: options.user});
        project.save({}, {success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_CREATED, {project: model})});
    }

    /**
     * Handle request Project delete.
     */
    _handleRequestProjectDelete(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, {title: 'Deleting Project', content: 'Please wait...'});
        this._activeProject = null;
        options.project.destroy({success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_DELETED, {project: model})});
    }

    /**
     * Handle request set active Project.
     */
    _handleRequestSetActiveProject(options)
    {
        this._activeProject = options.project;
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options)
    {
        this._activeProject = options.project;
        this._activeProject.fetch();
        var collection = new WorkflowRunCollection();
        collection.fetch({data: {project: this._activeProject.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [collection]});
        var layoutView = new LayoutViewModel({template: _.template($('#template-main_layoutview_model_inverse').text())});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: layoutView});
        layoutView.showItem(new ViewProject({model: this._activeProject}));
        layoutView.showCollection(new ViewWorkflowRunCollection({collection: collection}));
    }

    /**
     * Handle collection selection.
     */
    _handleEventCollectionSelected()
    {
        var collection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_PROJECT_COLLECTION);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [collection]});
        var view = new ViewProjectCollection({collection: collection});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: view});
    }

    /**
     * Handle request for current active project. Returns null.
     */
    _handleRequestProjectActive()
    {
        return this._activeProject;
    }

    /**
     * Handle project admins get success.
     */
    _handleProjectGetAdminsSuccess(response, collection)
    {
        collection.fetch({data: {username__in: response.join()}});
    }

    /**
     * Handle project workers get success.
     */
    _handleProjectGetWorkersSuccess(response, collection)
    {   
        if (response.flat().length !== 0){
            collection.fetch({data: {username__in: response.join()}});
        }
    }

    /**
     * Handle request to remove User as Project admin.
     * We have to use a custom AJAX call since modifying the users of a Project
     * has no endpoint at the moment.
     */
    _handleRequestRemoveUserAdmin(options)
    {
        var admins = options.project.get('admins');
        if (admins.length > 1)
        {
            var userIndex = admins.indexOf(options.user.get('username'));
            if (userIndex >= 0)
            {
                admins.splice(userIndex, 1);
                var usersSendObject = {};
                admins.map(function(value) { usersSendObject[value] = value; return value; });
                var ajaxSettings = {success: (response) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_REMOVED_USER_ADMIN, {project: options.project}),
                                    error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                                    type: 'PUT',
                                    dataType: 'json',
                                    data: usersSendObject,
                                    url: options.project.get('url') + 'admins/'};
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
            }
            else
            {
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, {content: 'An error occured trying to remove this User.'});
            }
        }
        else
        {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, {content: 'At least one project admin, the creator, must exist.'});
        }
    }

    /**
     * Handle request to remove User as Project worker.
     * We have to use a custom AJAX call since modifying the users of a Project
     * has no endpoint at the moment.
     */
    _handleRequestRemoveUserWorker(options)
    {
        var users = options.project.get('workers');
        if (users.length > 0)
        {
            var userIndex = users.indexOf(options.user.get('username'));
            if (userIndex >= 0)
            {
                users.splice(userIndex, 1);
                var usersSendObject = {};
                users.map(function(value) { usersSendObject[value] = value; return value; });
                var ajaxSettings = {success: (response) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_REMOVED_USER_WORKER, {project: options.project}),
                                    error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                                    type: 'PUT',
                                    dataType: 'json',
                                    data: usersSendObject,
                                    url: options.project.get('url') + 'workers/'};
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
            }
            else
            {
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_ERROR, {content: 'An error occured trying to remove this User.'});
            }
        }
    }

    /**
     * Handle project removed user.
     */
    _handleEventProjectRemovedUser(options)
    {
        this._activeProject.fetch();
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this._activeProject});
    }

    /**
     * Handle request add admin.
     */
    _handleRequestProjectAddUserAdmin(options)
    {
        var users = options.project.get('admins');
        users.push(options.username);
        var usersSendObject = {};
        users.map(function(value) { usersSendObject[value] = value; return value; });
        var ajaxSettings = {success: (response) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_ADDED_USER_ADMIN, {project: options.project}),
                            error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                            type: 'PUT',
                            dataType: 'json',
                            data: usersSendObject,
                            url: options.project.get('url') + 'admins/'};
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
     }

    /**
     * Handle request add worker.
     */
    _handleRequestProjectAddUserWorker(options)
    {
        var users = options.project.get('workers');
        users.push(options.username);
        var usersSendObject = {};
        users.map(function(value) { usersSendObject[value] = value; return value; });
        var ajaxSettings = {success: (response) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_ADDED_USER_WORKER, {project: options.project}),
                            error: (response) => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SYSTEM_HANDLE_ERROR, {response: response}),
                            type: 'PUT',
                            dataType: 'json',
                            data: usersSendObject,
                            url: options.project.get('url') + 'workers/'};
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_REQUEST_AJAX, {settings: ajaxSettings});
    }

    /**
     * Handle event added admin.
     */
    _handleEventProjectAddedUserAdmin()
    {
        this._activeProject.fetch();
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this._activeProject});
     }

    /**
     * Handle event added worker.
     */
    _handleEventProjectAddedUserWorker()
    {
        this._activeProject.fetch();
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this._activeProject});
    }
}
