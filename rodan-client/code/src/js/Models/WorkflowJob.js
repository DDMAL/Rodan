import $ from 'jquery';
import BaseModel from './BaseModel';
import InputPortCollection from 'js/Collections/InputPortCollection';
import OutputPortCollection from 'js/Collections/OutputPortCollection';

/**
 * WorkflowJob.
 */
export default class WorkflowJob extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize.
     *
     * @param {object} options Backbone.Model options object; 'options.input_ports' (InputPortCollection or associated Backbone.Collection raw-object representation) and 'options.output_ports' (OutputPortCollection or associated Backbone.Collection raw-object representation) must also be provided
     */
    initialize(options)
    {
        var inputPortCollection = new InputPortCollection();
        var outputPortCollection = new OutputPortCollection();
        inputPortCollection.set(options.input_ports);
        outputPortCollection.set(options.output_ports);
        this.set('input_ports', inputPortCollection);
        this.set('output_ports', outputPortCollection);
    }

    /**
     * Returns defaults.
     *
     * @return {object} object holding default values
     */
    defaults()
    {
        return {input_ports: null, output_ports: null, job_name: null, job_description: null};
    }

    /**
     * Override of Backbone.Model.parse. This will populate 'input_ports' and 'output_ports' with associated models.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        for (var i in response.input_ports)
        {
            var ModelClass = this.get('input_ports').model;
            var model = new ModelClass(response.input_ports[i]);
            this.get('input_ports').add(model, {merge: true});
        }
        response.input_ports = this.get('input_ports');

        for (i in response.output_ports)
        {
            var ModelClass = this.get('output_ports').model;
            var model = new ModelClass(response.output_ports[i]);
            this.get('output_ports').add(model, {merge: true});
        }
        response.output_ports = this.get('output_ports');

        return response;
    }

    /**
     * Returns UUID of associated Job.
     *
     * @return {string} UUID of associated Job
     */
    getJobUuid()
    {
        var lastSlash = this.get('job').lastIndexOf('/');
        var subString = this.get('job').substring(0, lastSlash);
        var secondLastSlash = subString.lastIndexOf('/');
        return this.get('job').substring(secondLastSlash + 1, lastSlash);
    }

    /**
     * Returns human-readable descriptive text.
     *
     * @return {string} 'name' and 'job_description' (from associated Job)
     */
    getDescription()
    {
        var string = this.get('name') + ': ' + this.get('job_description');
        return string;
    }

    /**
     * Returns true if this WorkflowJob has settings.
     *
     * @return {boolean} true if this WorkflowJob has settings
     */
    hasSettings()
    {
        return !$.isEmptyObject(this.get('job_settings'));
    }
}
WorkflowJob.prototype.routeName = 'workflowjobs';