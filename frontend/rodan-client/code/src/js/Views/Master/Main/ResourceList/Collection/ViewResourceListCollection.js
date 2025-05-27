import _ from 'underscore';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * View for ResourceList Collection.
 */
export default class ViewResourceListCollection extends BaseViewCollection
{
    /**
     * On render populate the ResourceTypeList dropdown.
     */
    onRender()
    {
 /*       var templateResourceType = _.template($('#template-resourcetype_collection_item').html());
        var resourceTypeCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
//        var html = templateResourceType({url: null, mimetype: 'Auto-detect', extension: 'Rodan will attempt to determine the file type based on the file itself'});
 //       this.$el.find('#select-resourcetype').append(html);
        for (var i = 0; i < resourceTypeCollection.length; i++)
        {
        	var resourceType = resourceTypeCollection.at(i);
            var html = templateResourceType(resourceType.attributes);
        	this.$el.find('#select-resourcetype').append(html);
        }*/
    }

    /**
     * Handle button new ResourceList.
     */
    _handleButtonNewResourceList()
    {
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCELIST_CREATE, {project: project});
    }
}
ViewResourceListCollection.prototype.behaviors = [{behaviorClass: BehaviorTable, table: '#table-resourcelists'}];
ViewResourceListCollection.prototype.ui = {
    buttonNewResourceList: '#button-new_resourcelist'
};
ViewResourceListCollection.prototype.events = {
    'click @ui.buttonNewResourceList': '_handleButtonNewResourceList'
};
