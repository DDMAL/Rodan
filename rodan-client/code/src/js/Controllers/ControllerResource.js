import $ from 'jquery';
import _ from 'underscore';
import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import Resource from 'js/Models/Resource';
import ResourceCollection from 'js/Collections/ResourceCollection';
import ViewDeleteConfirm from '../Views/Master/Main/Shared/ViewDeleteConfirm';
import ViewResource from 'js/Views/Master/Main/Resource/Individual/ViewResource';
import ViewResourceMulti from 'js/Views/Master/Main/Resource/Individual/ViewResourceMulti';
import ViewResourceCollection from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollection';
import ViewResourceCollectionItem from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollectionItem';
import ViewProject from '../Views/Master/Main/Project/Individual/ViewProject';

/**
 * Controller for Resources.
 */
export default class ControllerResource extends BaseController {
    initialize() {
        this._selectedResources = new Set();
        this._baseSelectResource = null;
    }
    ///////////////////////////////////////////////////////////////////////////////////////
    // PRIVATE METHODS
    ///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio() {
        // Events
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCE_SELECTED_COLLECTION, options => this._handleEventCollectionSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCE_SELECTED, options => this._handleEventItemSelected(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCE_CREATED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCE_DELETED, options => this._handleSuccessGeneric(options));
        Radio.channel('rodan').on(RODAN_EVENTS.EVENT__RESOURCE_SAVED, options => this._handleSuccessGeneric(options));

        // Requests
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_SHOWLAYOUTVIEW, options => this._handleCommandShowLayoutView(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_CREATE, options => this._handleRequestResourceCreate(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_DELETE, options => this._handleCommandResourceDelete(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_DELETE_CONFIRM, options => this._handleCommandResourceDeleteConfirm(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_DOWNLOAD, options => this._handleRequestResourceDownload(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_SAVE, options => this._handleCommandResourceSave(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCE_VIEWER_ACQUIRE, options => this._handleRequestViewer(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCES_LOAD, options => this._handleRequestResources(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCES_LOAD_NO_PAGE, options => this._handleRequestResourcesNoPagination(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__RESOURCES_CURRENT, options => this._handleCurrentResources(options));
    }

    /**
     * Handle show LayoutView.
     */
    _handleCommandShowLayoutView(options) {
        this._projectView = options.projectView;
    }

    /**
     * Handle collection selection.
     */
    _handleEventCollectionSelected(options) {
        this._collection = new ResourceCollection();
        this._collection.fetch({ data: { project: options.project.id } });

        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__UPDATER_SET_COLLECTIONS, { collections: [this._collection] });

        const activeProject = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        this._projectView = new ViewProject({ model: activeProject });

        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MAINREGION_SHOW_VIEW, { view: this._projectView });

        this._viewCollection = new ViewResourceCollection({ collection: this._collection });
        this._projectView.showCollection(this._viewCollection);
    }

    /**
     * Handle item selection.
     */
    _handleEventItemSelected(options) {
        if (!options.multiple && !options.range) {
            this._selectedResources.clear();
            this._baseSelectResource = null;
        }

        if (options.multiple && this._selectedResources.has(options.resource)) {
            this._selectedResources.delete(options.resource);
            this._baseSelectResource = null;
        } else if (options.range && this._baseSelectResource !== null) {
            let indexBase = this._collection.indexOf(this._baseSelectResource);
            let indexRes = this._collection.indexOf(options.resource);
            this._selectedResources.clear();
            for (let n = Math.min(indexBase, indexRes); n <= Math.max(indexBase, indexRes); n++) {
                this._selectedResources.add(this._collection.at(n));
            }
        } else {
            this._selectedResources.add(options.resource);
            this._baseSelectResource = options.resource;
        }

        if (this._selectedResources.size === 0) {
            this._projectView.clearCollectionItemInfoView();
        } else if (this._selectedResources.size === 1) {
            this._projectView.showCollectionItemInfo(new ViewResource({ model: this._selectedResources.values().next().value }));
        } else {
            this._projectView.showCollectionItemInfo(new ViewResourceMulti({ models: this._selectedResources }));
        }
    }

    /**
     * Handle command add Resource.
     */
    _handleRequestResourceCreate(options) {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Creating Resource', content: 'Please wait...' });
        var resource = null;
        let opts = {
            project: options.project.get('url'),
            file: options.file
        };
        if (options.resourcetype) {
            opts['resource_type'] = options.resourcetype;
        }
        if (options.label_names !== undefined) {
            opts['label_names'] = options.label_names;
        }
        resource = new Resource(opts);
        var jqXHR = resource.save({}, { success: model => this._handleCreateSuccess(model, this._collection) });
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__TRANSFERMANAGER_MONITOR_UPLOAD, { request: jqXHR, file: options.file });
    }

    /**
     * Handle command delete Resource.
     */
    _handleCommandResourceDelete(options) {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Deleting Resource', content: 'Please wait...' });
        this._projectView.clearCollectionItemInfoView();
        if (options.resource.size) {
            options.resource.forEach(resource => resource.destroy({ success: model => this._handleDeleteSuccess(model, this._collection) }));
        } else {
            options.resource.destroy({ success: model => this._handleDeleteSuccess(model, this._collection) });
        }
    }

    /**
     * Handle command delete Resource confirm modal window.
     */
    _handleCommandResourceDeleteConfirm(options) {
        console.log(options.resource.size);
        let names = options.resource.size ? [...options.resource].map(resource => resource.get('name')) : options.resource.get('name');
        console.log(names);
        var view = new ViewDeleteConfirm({
            type: 'resource',
            names: names,
            toDelete: options.resource
        });
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {
            content: view,
            title: 'Deleting Resource'
        });
    }

    /**
     * Handle command download Resource.
     */
    _handleRequestResourceDownload(options) {
        var mimetype = options.resource.get('resource_type_full').mimetype;
        var ext = options.resource.get('resource_type_full').extension;
        var filename = options.resource.get('name') + '.' + ext;
        let a = document.createElement('a');
        a.href = options.resource.get('download');
        a.download = filename;
        a.type = mimetype;
        document.body.append(a);
        a.click();
        a.remove();
    }

    /**
     * Handle command save Resource.
     */
    _handleCommandResourceSave(options) {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, { title: 'Saving Resource', content: 'Please wait...' });
        options.resource.save(options.fields, { patch: true, success: model => Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_SAVED, { resource: model }) });
    }

    _handleCurrentResources(options) {
        try {
            if (this._collection_no_page['_lastData']['project'] === options.data.project) {
                return this._collection_no_page;
            } else {
                return this._handleRequestResourcesNoPagination(options);
            }
        } catch (e) {
            console.debug(e);
            return this._handleRequestResources(options);
        }
    }

    /**
     * Handle request Resources.
     */
    _handleRequestResources(options) {
        this._collection = new ResourceCollection();
        this._collection.fetch(options);
        return this._collection;
    }

    /**
     * Handle request Resources.
     */
    _handleRequestResourcesNoPagination(options) {
        options.data.no_page = true;
        options.async = false;
        this._collection_no_page = new ResourceCollection();
        this._collection_no_page.fetch(options);
        return this._collection_no_page;
    }

    /**
     * Handle request for Resource viewer.
     */
    _handleRequestViewer(options) {
        var ajaxOptions = {
            url: options.resource.get('url') + 'acquire/',
            type: 'POST',
            dataType: 'json',
            success: response => this._handleSuccessAcquire(response)
        };
        $.ajax(ajaxOptions);
    }

    /**
     * Handle acquire success.
     */
    _handleSuccessAcquire(response) {
        window.open(response.working_url, '', '_blank');
    }

    /**
     * Handle create success.
     */
    _handleCreateSuccess(resource, collection) {
        collection.add(resource);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_CREATED, { resource: resource });
    }

    /**
     * Handle delete success.
     */
    _handleDeleteSuccess(model, collection) {
        collection.remove(model);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_DELETED, { resource: model });
    }

    /**
     * Handle generic success.
     */
    _handleSuccessGeneric(options) {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABELS_LOAD, {});
    }
}
