import $ from 'jquery';
import _ from 'underscore';
import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import LayoutViewModel from 'js/Views/Master/Main/LayoutViewModel';
import LayoutViewResourceAssignment from 'js/Views/Master/Main/ResourceAssignment/LayoutViewResourceAssignment';
import Radio from 'backbone.radio';
import ResourceCollection from 'js/Collections/ResourceCollection';
import ResourceList from 'js/Models/ResourceList';
import ResourceListCollection from 'js/Collections/ResourceListCollection';
import ViewResourceCollectionModal from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollectionModal';
import ViewResourceList from 'js/Views/Master/Main/ResourceList/Individual/ViewResourceList';
import ViewResourceListCollection from 'js/Views/Master/Main/ResourceList/Collection/ViewResourceListCollection';
import ViewResourceListCollectionItem from 'js/Views/Master/Main/ResourceList/Collection/ViewResourceListCollectionItem';

/**
 * Controller for ResourceLists.
 */
export default class ControllerResourceList extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        // Events
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED_COLLECTION, options => this._handleEventCollectionSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED, options => this._handleEventItemSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCELIST_CREATED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCELIST_DELETED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCELIST_SAVED, options => this._handleSuccessGeneric(options));

        // Requests
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_ADD_RESOURCE, options => this._handleRequestAddResource(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_CREATE, options => this._handleRequestResourceListCreate(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_DELETE, options => this._handleCommandResourceListDelete(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_DOWNLOAD, options => this._handleRequestResourceListDownload(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_REMOVE_RESOURCE, options => this._handleRequestRemoveResource(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_SAVE, options => this._handleCommandResourceListSave(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELIST_SHOW_RESOURCEASSIGNMENT_VIEW, options => this._handleRequestShowResourceAssignmentView(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCELISTS_LOAD, options => this._handleRequestLoad(options));
    }

    /**
     * Handle show LayoutView.
     */
 /*   _handleCommandShowLayoutView(options)
    {
        this._layoutView = options.layoutView;
    }*/

    /**
     * Handle request add Resource.
     */
    _handleRequestAddResource(options)
    {
        debugger;
    }

    /**
     * Handle request remove Resource.
     */
    _handleRequestRemoveResource(options)
    {
        debugger;
    }

    /**
     * Handle request show Resource assignment view.
     */
    _handleRequestShowResourceAssignmentView(options)
    {
        // Get ResourceType (if it exists).
        var resourceTypeId = null;
        var globalResourceTypes = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
        if (options.resourcelist.has('resource_type'))
        {
            resourceTypeId = globalResourceTypes.findWhere({url: options.resourcelist.get('resource_type')}).id;
        }

        // Get available Resources.
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        var data = {project: project.id, resource_type: null};
        var availableResources = new ResourceCollection();
        availableResources.fetch({data: data});

        // Get Collections.
        // Issue #113: https://github.com/DDMAL/rodan-client/issues/113
        // What's the best way to get Resource objects for a ResourceList.
        var assignedResources = new ResourceCollection();

        // Create views.
        var assignedResourceView = new ViewResourceCollectionModal({collection: assignedResources,
                                                                    childViewOptions: {assigned: true,
                                                                                       requestdata: {resourcelist: options.resourcelist},
                                                                                       assignrequest: RODAN_EVENTS.REQUEST__RESOURCELIST_ADD_RESOURCE,
                                                                                       unassignrequest: RODAN_EVENTS.REQUEST__RESOURCELIST_REMOVE_RESOURCE}});
        var resourceListView = new ViewResourceCollectionModal({collection: availableResources,
                                                                childViewOptions: {assigned: false,
                                                                                   requestdata: {resourcelist: options.resourcelist},
                                                                                   assignrequest: RODAN_EVENTS.REQUEST__RESOURCELIST_ADD_RESOURCE,
                                                                                   unassignrequest: RODAN_EVENTS.REQUEST__RESOURCELIST_REMOVE_RESOURCE}});

        // Show the layout view.
        var view = new LayoutViewResourceAssignment({viewavailableresources: resourceListView, viewassignedresources: assignedResourceView});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {content: view, title: 'Resource List'});
    }

    /**
     * Handle collection selection.
     */
    _handleEventCollectionSelected(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELISTS_LOAD, {data: {project: options.project.id}});
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, {collections: [this._collection]});
        this._layoutView = new LayoutViewModel();
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, {view: this._layoutView});
        var view = new ViewResourceListCollection({collection: this._collection,
                                                   template: _.template($('#template-main_resourcelist_collection').text()),
                                                   childView: ViewResourceListCollectionItem,
                                                   model: options.project});
        this._layoutView.showCollection(view);
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options)
    {
        this._layoutView.showItem(new ViewResourceList({model: options.resourcelist}));
    }

    /**
     * Handle command add Resource.
     */
    _handleRequestResourceListCreate(options)
    {
        var resourceList = new ResourceList({project: options.project.get('url'), name: 'untitled'});
        resourceList.save({}, {success: (model) => this._handleCreateSuccess(model, this._collection)});
    }

    /**
     * Handle command delete ResourceList.
     */
    _handleCommandResourceListDelete(options)
    {
        this._layoutView.clearItemView();
        options.resourcelist.destroy({success: (model) => this._handleDeleteSuccess(model, this._collection)});
    }

    /**
     * Handle command download ResourceList.
     */
    _handleRequestResourceListDownload(options)
    {
        //var mimetype = options.resource.get('resource_type_full').mimetype;
        //var ext = options.resource.get('resource_type_full').extension;
//        var filename = options.resource.get('name') + '.zip';
  //      Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__TRANSFERMANAGER_DOWNLOAD, {url: options.resource.get('download'), filename: filename, mimetype: mimetype});
    }

    /**
     * Handle command save Resource.
     */
    _handleCommandResourceListSave(options)
    {
        options.resourcelist.save(options.fields, {patch: true, success: (model) => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SAVED, {resourcelist: model})});
    }

    /**
     * Handle request load.
     */
    _handleRequestLoad(options)
    {
        this._collection = new ResourceListCollection();
        this._collection.fetch(options);
        return this._collection;
    }

    /**
     * Handle create success.
     */
    _handleCreateSuccess(model, collection)
    {
        collection.add(model);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_CREATED, {resourcelist: model});
    }

    /**
     * Handle delete success.
     */
    _handleDeleteSuccess(model, collection)
    {
        collection.remove(model);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_DELETED, {resourcelist: model});
    }

    /**
     * Handle generic success.
     */
    _handleSuccessGeneric(options)
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
    }
}
