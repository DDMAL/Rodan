import $ from 'jquery';
import _ from 'underscore';
import tagsInput from 'tags-input';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewResourceTypeCollectionItem from 'js/Views/Master/Main/ResourceType/ViewResourceTypeCollectionItem';

/**
 * Resource Multi-Select View
 */
export default class ViewResourceMulti extends Marionette.CollectionView
{
    constructor(options) {
        super(options);
        this._models = options.models;

        var rtUrl;
        var labels;
        this.labelNames = '';
        this.isSameType = true;
        this.isSameLabel = true;

        for (let model of this._models) {
            let modelResourceTypeURL = model.get('resource_type');
            let modelLabels = model.get('labels');
            if (rtUrl === undefined) {
                rtUrl = modelResourceTypeURL;
            }
            else if (rtUrl !== modelResourceTypeURL) {
                this.isSameType = false;
            }
            if (labels === undefined) {
                labels = modelLabels;
                this.labelNames = model.get('resource_label_full');
            }
            else if (!_.isEqual(labels, modelLabels)) {
                this.isSameLabel = false;
            }
        }

        this.collection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
        this.collection.each(function(model) { model.unset('selected'); });
        var resourceType = this.collection.findWhere({url: rtUrl});
        resourceType.set('selected', 'selected');
    }
    /**
     * Initialize buttons after render.
     */
    onRender()
    {
        var disabledDelete = false;
        var disabledDownload = false;
        for (var model of this._models) {
            if (model.get('origin') !== null) {
                disabledDelete = true;
            }
            if (model.get('download') === null) {
                disabledDownload = true;
            }
        }
        $(this.ui.buttonDelete).attr('disabled', disabledDelete);
        $(this.ui.buttonDownload).attr('disabled', disabledDownload);

        $(this.ui.buttonSave).attr('disabled', !this.isSameType);
        $(this.ui.selectResourceType).attr('disabled', !this.isSameType);

        // Disable all other buttons for now.
        $(this.ui.buttonView).attr('disabled', true);
    }

    onAttach()
    {
        if (this.isSameLabel) {
          this.ui.labelInput[0].setAttribute('value', _.map(this.labelNames, (label) => { return label.name; }));
          tagsInput(this.ui.labelInput[0]);
        }
    }

    templateContext() {
        return {
            count: this._models.size,
            isSameLabel: this.isSameLabel
        };
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle button delete.
     */
    _handleClickButtonDelete()
    {
        for (var model of this._models) {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_DELETE, {resource: model});
        }
    }

    _handleClickButtonDownload()
    {
        let modelArray = [...this._models.values()];
        let uuids = _.map(modelArray, val => { return val.id; });
        let baseUrl = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__SERVER_GET_ROUTE, 'resource-archive');
        let a = document.createElement('a');
        a.download = 'Archive.zip';
        a.href = baseUrl + '?' + $.param({resource_uuid: uuids}, true);
        document.body.append(a);
        a.click();
        a.remove();
    }

    _handleClickButtonSave()
    {
        let fields = {
            resource_type: this.ui.selectResourceType.find(':selected').val()
        };
        if (this.isSameLabel) {
            fields['label_names'] = this.ui.labelInput.val();
        }
        for (var model of this._models) {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_SAVE, {resource: model, fields: fields});
        }
    }
}
ViewResourceMulti.prototype.modelEvents = {
};
ViewResourceMulti.prototype.ui = {
    buttonSave: '#button-main_resource_individual_save',
    buttonDelete: '#button-main_resource_individual_delete',
    buttonDownload: '#button-main_resource_individual_download',
    buttonView: '#button-main_resource_individual_view',
    selectResourceType: '#select-resourcetype',
    labelInput: '#label-multi-input'
};
ViewResourceMulti.prototype.events = {
    'click @ui.buttonDelete': '_handleClickButtonDelete',
    'click @ui.buttonDownload': '_handleClickButtonDownload',
    'click @ui.buttonSave': '_handleClickButtonSave'
};
ViewResourceMulti.prototype.template = _.template($('#template-main_resource_individual_multi').text());
ViewResourceMulti.prototype.childView = ViewResourceTypeCollectionItem;
ViewResourceMulti.prototype.childViewContainer = '#select-resourcetype';
