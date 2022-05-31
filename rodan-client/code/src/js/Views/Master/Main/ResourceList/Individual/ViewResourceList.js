import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewResourceTypeCollectionItem from 'js/Views/Master/Main/ResourceType/ViewResourceTypeCollectionItem';

/**
 * ResourceList view.
 */
export default class ViewResourceList extends Marionette.CollectionView
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        /** @ignore */
        this.collection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
        this.collection.each(function(model) { model.unset('selected'); });
      //  var resourceType = this.collection.findWhere({url: this.model.get('resource_type')});
       // resourceType.set('selected', 'selected');
    }

    /**
     * Initialize buttons after render.
     */
    onRender()
    {
        var disabledDelete = this.model.get('origin') !== null;
        $(this.ui.buttonDelete).attr('disabled', disabledDelete); 
        var disabledDownload = this.model.get('download') === null;
        $(this.ui.buttonDownload).attr('disabled', disabledDownload); 
        var disableView = this.model.get('viewer_url') === null || disabledDownload;
        $(this.ui.buttonView).attr('disabled', disableView);
    }

    /**
     * Destroy callback.
     */
    onDestroy()
    {
        this.collection = null;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button save.
     */
    _handleClickButtonSave()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_SAVE, {resourcelist: this.model,
                                                                                 fields: {resource_type: this.ui.selectResourceType.val(),
                                                                                          name: this.ui.resourceListName.val(),
                                                                                          description: this.ui.resourceListDescription.val()}});
    }

    /**
     * Handle button delete.
     */
    _handleClickButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_DELETE, {resourcelist: this.model});
    }

    /**
     * Handle button download.
     */
    _handleClickDownload()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_DOWNLOAD, {resourcelist: this.model});
    }

    /**
     * Handle button add/remove.
     */
     _handleClickAddRemove()
     {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_SHOW_RESOURCEASSIGNMENT_VIEW, {resourcelist: this.model});
     }
}
ViewResourceList.prototype.modelEvents = {
    'all': 'render'
};
ViewResourceList.prototype.ui = {
    buttonSave: '#button-main_resourcelist_individual_save',
    buttonDelete: '#button-main_resourcelist_individual_delete',
    selectResourceType: '#select-resourcetype',
    resourceListName: '#text-resourcelist_name',
    resourceListDescription: '#text-resourcelist_description',
    buttonDownload: '#button-main_resourcelist_individual_download',
    buttonAddRemove: '#button-main_resourcelist_individual_addremove'
};
ViewResourceList.prototype.events = {
    'click @ui.buttonSave': '_handleClickButtonSave',
    'click @ui.buttonDelete': '_handleClickButtonDelete',
    'click @ui.buttonDownload': '_handleClickDownload',
    'click @ui.buttonAddRemove': '_handleClickAddRemove'
};
ViewResourceList.prototype.template = _.template($('#template-main_resourcelist_individual').text());
ViewResourceList.prototype.childView = ViewResourceTypeCollectionItem;
ViewResourceList.prototype.childViewContainer = '#select-resourcetype';
