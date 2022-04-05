import $ from 'jquery';
import _ from 'underscore';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import ViewWorkflowRunCollectionItem from './ViewWorkflowRunCollectionItem';

/**
 * WorkflowRun Collection view.
 */
export default class ViewWorkflowRunCollection extends BaseViewCollection {}
ViewWorkflowRunCollection.prototype.template = _.template($('#template-main_workflowrun_collection').text());
ViewWorkflowRunCollection.prototype.childView = ViewWorkflowRunCollectionItem;
ViewWorkflowRunCollection.prototype.behaviors = [{behaviorClass: BehaviorTable, table: '#table-workflowruns'}];
ViewWorkflowRunCollection.prototype.filterTitles = {
    'creator__username': 'Creator'
};
