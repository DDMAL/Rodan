import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import 'json-editor';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Settings view for WorkflowJob.
 */
export default class ViewSettings extends Marionette.View
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflow' (Workflow) must also be provided
     */
    initialize(options)
    {
        this._workflow = options.workflow;
    }

    /**
     * Initialize the settings after render.
     */
    onRender()
    {
        this._initializeSettingsDisplay();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Save settings.
     */
    _handleButtonSave()
    {
        var element = this._getJQueryElement();
        if ($(element).is(':visible'))
        {
            this.model.set('job_settings', this._editor.getValue());
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__WORKFLOWJOB_SAVE, {workflowjob: this.model, workflow: this._workflow});
        }
    }

    /**
     * Initializes settings display.
     */
    _initializeSettingsDisplay()
    {
        // Initially hide.
        var element = this._getJQueryElement();
        $(element).hide();

        // Create settings.
        var startValues = this.model.get('job_settings');
        startValues = $.isEmptyObject(startValues) ? null : startValues;
        $(element).show();
        var jobUuid = this.model.getJobUuid();
        var collection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION);
        var job = collection.get(jobUuid);
        var settingsSchema = {
            schema: job.get('settings'),
            theme: 'bootstrap3',
            disable_collapse: true,
            disable_edit_json: true,
            disable_properties: true,
            no_additional_properties: true,
            show_errors: 'always',
            startval: startValues,
            form_name_root: ' '
        };
        this._editor = new JSONEditor(element, settingsSchema);
    }

    /**
     * Get HTML element as jQuery object.
     */
    _getJQueryElement()
    {
        return $(this.$el.find('#workflowjob-settings')[0])[0];
    }
}
ViewSettings.prototype.modelEvents = {
    'all': 'render'
};
ViewSettings.prototype.ui = {
    buttonSave: '#button-save_workflowjob_settings'
        };
ViewSettings.prototype.events = {
    'click @ui.buttonSave': '_handleButtonSave'
        };
ViewSettings.prototype.template = _.template($('#template-main_workflowjob_settings').text());
