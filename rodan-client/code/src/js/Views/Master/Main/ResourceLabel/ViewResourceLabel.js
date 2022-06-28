import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';


/**
 * ResourceLabel view
 */
export default class ViewResourceLabel extends Marionette.View
{
    initialize(object)
    {
        this.model = object.model;
    }

    templateContext()
    {
        return {
            tagName: this.model.get('name')
        }
    }

    _handleClickButtonSave()
    {
        let newName = $(this.ui.nameInput).val();
        this.model.save({name: newName}, {
            patch: true,
            success: () => {
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCES_UPDATE_LABELS);
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
            },
            error: () => {
                $(this.ui.alert).removeAttr('hidden');
            }});
    }
}
ViewResourceLabel.prototype.ui = {
    buttonSave: '#button-save_label_name',
    nameInput: '#text-label_name',
    alert: '#alert-label_exists'
};
ViewResourceLabel.prototype.events = {
    'click @ui.buttonSave': '_handleClickButtonSave'
};
ViewResourceLabel.prototype.template = _.template($('#template-main_resourcelabel').text());
