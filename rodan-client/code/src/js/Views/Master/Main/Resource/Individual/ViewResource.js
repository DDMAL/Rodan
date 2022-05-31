import $ from 'jquery';
import _ from 'underscore';
import tagsInput from 'tags-input';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewResourceLabel from 'js/Views/Master/Main/ResourceLabel/ViewResourceLabel';
import ViewResourceTypeCollectionItem from 'js/Views/Master/Main/ResourceType/ViewResourceTypeCollectionItem';

/**
 * Resource view.
 */
export default class ViewResource extends Marionette.CollectionView
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
        var resourceType = this.collection.findWhere({url: this.model.get('resource_type')});
        resourceType.set('selected', 'selected');
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

        if (this.isAttached()) {
            tagsInput(this.ui.resourceLabels[0]);
        }
    }

    /**
     * Initialize label field after it's attached to the DOM
     */
    onAttach()
    {
        tagsInput(this.ui.resourceLabels[0]);
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
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_SAVE, {resource: this.model,
                                                                             fields: {resource_type: this.ui.selectResourceType.find(':selected').val(),
                                                                                      name: _.escape(this.ui.resourceName.val()),
                                                                                      description: _.escape(this.ui.resourceDescription.val()),
                                                                                      label_names: _.escape(this.ui.resourceLabels.val())}});
    }

    /**
     * Handle button delete.
     */
    _handleClickButtonDelete()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_DELETE, {resource: this.model});
    }

    /**
     * Handle button download.
     */
    _handleClickDownload()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_DOWNLOAD, {resource: this.model});
    }

    /**
     * Handle button view.
     */
    _handleClickView()
    {
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_VIEWER_ACQUIRE, {resource: this.model});
    }

    _handleDblClickTag(evt)
    {
        let labels = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABEL_COLLECTION);
        let model = labels.findWhere({name: evt.target.textContent});
        if (model) {
            let view = new ViewResourceLabel({model: model});
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {
                content: view
            });
        }
    }
}
ViewResource.prototype.modelEvents = {
    'all': 'render'
};
ViewResource.prototype.ui = {
    buttonSave: '#button-main_resource_individual_save',
    buttonDelete: '#button-main_resource_individual_delete',
    selectResourceType: '#select-resourcetype',
    resourceName: '#text-resource_name',
    resourceDescription: '#text-resource_description',
    buttonDownload: '#button-main_resource_individual_download',
    buttonView: '#button-main_resource_individual_view',
    resourceLabels: '#input-resource_labels',
    tagSpans: 'span.tag'
};
ViewResource.prototype.events = {
    'click @ui.buttonSave': '_handleClickButtonSave',
    'click @ui.buttonDelete': '_handleClickButtonDelete',
    'click @ui.buttonDownload': '_handleClickDownload',
    'click @ui.buttonView': '_handleClickView',
    'dblclick @ui.tagSpans': '_handleDblClickTag'
};
ViewResource.prototype.template = _.template($('#template-main_resource_individual').text());
ViewResource.prototype.childView = ViewResourceTypeCollectionItem;
ViewResource.prototype.childViewContainer = '#select-resourcetype';
