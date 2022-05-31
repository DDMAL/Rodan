import $ from 'jquery';
import _ from 'underscore';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import ViewProjectCollectionItem from './ViewProjectCollectionItem';

/**
 * Project Collection view.
 */
export default class ViewProjectCollection extends BaseViewCollection
{
    _handleButtonNewProject()
    {
        var user = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__AUTHENTICATION_USER);
        Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__PROJECT_CREATE, {creator: user});
    }
}

ViewProjectCollection.prototype.ui = {
    buttonNewProject: '#button-new_project'
};
ViewProjectCollection.prototype.events = {
    'click @ui.buttonNewProject': '_handleButtonNewProject'
};
ViewProjectCollection.prototype.template = _.template($('#template-main_project_collection').text());
ViewProjectCollection.prototype.childView = ViewProjectCollectionItem;
ViewProjectCollection.prototype.behaviors = [
    {
        behaviorClass: BehaviorTable,
        table: '#table-projects'
    }
];
