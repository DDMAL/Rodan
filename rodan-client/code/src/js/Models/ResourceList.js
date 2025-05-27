import BaseModel from './BaseModel';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import ResourceCollection from 'js/Collections/ResourceCollection';

/**
 * ResourceList.
 */
export default class ResourceList extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     *
     * @param {object} options Backbone.Model options object
     */
    initialize(options)
    {
        this._updateResourceTypeFull();
        this.on('change:resource_type', () => this._updateResourceTypeFull());

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
            updated: null
        };
    }

    /**
     * Returns UUID of associated ResourceType.
     *
     * @return {string} UUID of associated ResourceType; null if DNE
     */
    getResourceTypeUuid()
    {
        if (this.get('resource_type'))
        {
            var lastSlash = this.get('resource_type').lastIndexOf('/');
            var subString = this.get('resource_type').substring(0, lastSlash);
            var secondLastSlash = subString.lastIndexOf('/');
            return this.get('resource_type').substring(secondLastSlash + 1, lastSlash);
        }
        return null;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Updates full description of resource type.
     */
    _updateResourceTypeFull()
    {
        var resourceTypeId = this.getResourceTypeUuid();
        var jsonString = {};
        if (resourceTypeId !== null)
        {
            var resourceTypeCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
            jsonString = resourceTypeCollection.get(resourceTypeId).toJSON();
        }
        this.set('resource_type_full', jsonString); 
    }
}
ResourceList.prototype.routeName = 'resourcelists';