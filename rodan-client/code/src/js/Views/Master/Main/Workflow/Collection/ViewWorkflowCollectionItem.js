import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * View for Workflow Collection.
 */
export default class ViewWorkflowCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles click.
     */
    _handleClick()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED, {workflow: this.model});
    }

    /**
     * Handle double-click.
     */
    _handleDoubleClick()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWBUILDER_SELECTED, {workflow: this.model});
    }
}
ViewWorkflowCollectionItem.prototype.template = _.template($('#template-main_workflow_collection_item').text());
ViewWorkflowCollectionItem.prototype.tagName = 'tr';
ViewWorkflowCollectionItem.prototype.events = {
    'click': '_handleClick',
    'dblclick': '_handleDoubleClick'
};
