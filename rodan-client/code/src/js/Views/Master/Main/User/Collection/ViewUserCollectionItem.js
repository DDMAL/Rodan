import BaseViewCollectionItem from 'js/Views/Master/Main/BaseViewCollectionItem';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * Item view for User Collection.
 */
export default class ViewUserCollectionItem extends BaseViewCollectionItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.project' (Project) must also be provided for the associated Project; if 'options.admin' is true, user treated as Project 'admin', else 'worker'
     */
    initialize(options)
    {
        this._project = options.project;
        this._removeEvent = options.admin ? RODAN_EVENTS.REQUEST__PROJECT_REMOVE_USER_ADMIN : RODAN_EVENTS.REQUEST__PROJECT_REMOVE_USER_WORKER;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle remove button.
     */
    _handleClickButtonRemove()
    {
        Radio.channel('rodan').request(this._removeEvent, {user: this.model, project: this._project});
    }
}
ViewUserCollectionItem.prototype.ui = {
    buttonRemove: '#button-main_project_remove_user'
};
ViewUserCollectionItem.prototype.events = {
    'click @ui.buttonRemove': '_handleClickButtonRemove'
};