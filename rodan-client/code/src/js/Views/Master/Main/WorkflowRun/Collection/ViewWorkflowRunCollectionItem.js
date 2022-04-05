import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * WorkflowRun Collection item view.
 */
export default class ViewWorkflowRunCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handles double click.
     */
    _handleDoubleClick()
    {
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOWRUN_SELECTED, {workflowrun: this.model});
    }
}
ViewWorkflowRunCollectionItem.prototype.template = _.template($('#template-main_workflowrun_collection_item').text());
ViewWorkflowRunCollectionItem.prototype.tagName = 'tr';
ViewWorkflowRunCollectionItem.prototype.events = {
    'dblclick': '_handleDoubleClick'
};
