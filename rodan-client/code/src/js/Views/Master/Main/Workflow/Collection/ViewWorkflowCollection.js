import $ from 'jquery';
import _ from 'underscore';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import ViewWorkflowCollectionItem from './ViewWorkflowCollectionItem';

/**
 * Workflow Collection view.
 */
export default class ViewWorkflowCollection extends BaseViewCollection
{
    _handleButtonNewWorkflow()
    {
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_CREATE, {project: project});
    }

    _handleButtonImportWorkflow()
    {
        var project = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_GET_ACTIVE);
        for (var i = 0; i < this.ui.fileInput[0].files.length; i++)
        {
        	var file = this.ui.fileInput[0].files[i];
    	    Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOW_IMPORT, {project: project, file: file});
    	}
	    this.ui.fileInput.replaceWith(this.ui.fileInput = this.ui.fileInput.clone(true));
    }
}
ViewWorkflowCollection.prototype.template = _.template($('#template-main_workflow_collection').text());
ViewWorkflowCollection.prototype.childView = ViewWorkflowCollectionItem;
ViewWorkflowCollection.prototype.behaviors = [{behaviorClass: BehaviorTable, table: '#table-workflows'}];
ViewWorkflowCollection.prototype.ui = {
    newWorkflowButton: '#button-new_workflow',
    fileInput: '#file-import_workflow'
};
ViewWorkflowCollection.prototype.events = {
    'click @ui.newWorkflowButton': '_handleButtonNewWorkflow',
    'change @ui.fileInput': '_handleButtonImportWorkflow'
};
ViewWorkflowCollection.prototype.filterTitles = {
    'creator__username': 'Creator'
};
