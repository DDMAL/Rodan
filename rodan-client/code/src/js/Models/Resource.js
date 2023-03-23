import Backbone from 'backbone';
import Radio from 'backbone.radio';
import _ from 'underscore';

import BaseModel from './BaseModel';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * Resource.
 */
export default class Resource extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     */
    initialize()
    {
        this._updateResourceTypeFull();
        this.set('download', this._getDownloadUrl());
        this.on('change:resource_type', () => { this._updateResourceTypeFull(); this._updateResourceLabelsFull() });
        this.on('change:resource_file', () => this.set('download', this._getDownloadUrl()));

        this._updateResourceLabelsFull();
        this.on('change:labels', () => this._updateResourceLabelsFull());

        // If the creator is null (i.e. was not uploaded by a person), inject a dummy.
        if (this.get('creator') === null)
        {
            this.set('creator', 'generated result');
        }
    }

    /**
     * Override of Backbone.Model.parse. If the 'creator' is null it gets set to 'generated result'.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        if (response.creator === null)
        {
            response.creator = 'generated result';
        }
        return response;
    }

    /**
     * Returns defaults.
     *
     * @return {object} object holding default values
     */
    defaults()
    {
        return {
            creator: {first_name: null, last_name: null, username: null},
            created: null,
            updated: null,
            labels: [],
            resource_label_full: ''
        };
    }

    /**
     * Override of Backbone.Model.sync. This is done to facilitate file uploads.
     *
     * @param {string} method synce method (@see Backbone.sync)
     * @param {object} model JavaScript object that holds properties for Resource
     * @param {object} options options to be passed to the AJAX call
     * @return {object} XmlHttpRequest instance
     */
    sync(method, model, options)
    {
        if (method === 'create')
        {
            var formData = new FormData();
            formData.append('project', model.get('project'));
            formData.append('files', model.get('file'));
            formData.append('label_names', model.get('label_names'));
            if (model.has('resource_type'))
            {
                formData.append('type', model.get('resource_type'));
            }
            if (model.has('label_names'))
            {
                formData.append('label_names', model.get('label_names'));
                model.unset('label_names');
            }
            if (model.has('label_uuids'))
            {
                formData.append('label_uuids', model.get('label_uuids'));
                model.unset('label_uuids');
            }

            // Set processData and contentType to false so data is sent as FormData
            _.defaults(options || (options = {}), {
                url: this.url(),
                data: formData,
                processData: false,
                contentType: false
            });
        }
        return Backbone.sync.call(this, method, model, options);
    }

    /**
     * Returns UUID of associated ResourceType.
     *
     * @return {string} UUID of associated ResourceType; null if DNE
     */
    getResourceTypeUuid()
    {
        if (this.get('resource_type') !== undefined)
        {
            var lastSlash = this.get('resource_type').lastIndexOf('/');
            var subString = this.get('resource_type').substring(0, lastSlash);
            var secondLastSlash = subString.lastIndexOf('/');
            return this.get('resource_type').substring(secondLastSlash + 1, lastSlash);
        }
        return null;
    }

    /**
     * Returns UUID from a ResourceLabel URL.
     *
     * @return {string} UUID of a ResourceLabel.
     */
    getResourceLabelUuid(url)
    {
        var lastSlash = url.lastIndexOf('/');
        var subString = url.substring(0, lastSlash);
        var secondLastSlash = subString.lastIndexOf('/');
        return url.substring(secondLastSlash + 1, lastSlash);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Updates full description of resource type.
     */
    _updateResourceTypeFull()
    {
        var resourceTypeCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
        var resourceTypeId = this.getResourceTypeUuid();
        var jsonString = {};
        if (resourceTypeId !== null)
        {
            jsonString = resourceTypeCollection.get(resourceTypeId).toJSON();
        }
        this.set('resource_type_full', jsonString);
    }

    /**
     * Updates label names.
     */
    _updateResourceLabelsFull()
    {
        var resourceLabelCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABEL_COLLECTION);
        let success = () => {
            let jsonStrings = [];
            let resourceLabelIds = this.get('labels').map(url => this.getResourceLabelUuid(url));
            resourceLabelIds.forEach(id => {
              let val = resourceLabelCollection.get(id);
              if (val)
              {
                  jsonStrings.push(val.toJSON());
              }
              else
              {
                  console.warn("skipping label with id " + id);
              }
            });
            this.set('resource_label_full', jsonStrings);
        };
        if (this.get('labels').length !== 0)
        {
            resourceLabelCollection.fetch({
                data: {
                    disable_pagination: true
                },
                success: success.bind(this)
            });
        }
    }

    /**
     * Returns download URL.
     */
    _getDownloadUrl()
    {
        if (this.get('resource_file'))
        {
            return this.get('resource_file');
        }
        return null;
    }
}
Resource.prototype.routeName = 'resources';
