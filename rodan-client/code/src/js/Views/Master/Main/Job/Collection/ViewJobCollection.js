import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import ViewJobCollectionItem from './ViewJobCollectionItem';

/**
 * View for Job Collection.
 */
export default class ViewJobCollection extends BaseViewCollection {}
ViewJobCollection.prototype.template = _.template($('#template-main_job_collection').text());
ViewJobCollection.prototype.childView = ViewJobCollectionItem;
//let Behavior = BehaviorTable.extend({'table': '#table-jobs'});
ViewJobCollection.prototype.behaviors = [
    {
        behaviorClass: BehaviorTable,
        table: '#table-jobs'
    }
];
