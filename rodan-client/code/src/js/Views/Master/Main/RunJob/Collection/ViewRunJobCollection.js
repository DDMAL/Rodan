import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import BehaviorTable from 'js/Behaviors/BehaviorTable';

/**
 * RunJob Collection view.
 */
export default class ViewRunJobCollection extends BaseViewCollection {}
ViewRunJobCollection.prototype.behaviors = [{behaviorClass: BehaviorTable, table: '#table-runjobs'}];
