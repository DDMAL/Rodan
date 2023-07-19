import BaseModel from './BaseModel';
import ConnectionCollection from 'js/Collections/ConnectionCollection';
import InputPortCollection from 'js/Collections/InputPortCollection';
import OutputPortCollection from 'js/Collections/OutputPortCollection';
import WorkflowJobCollection from 'js/Collections/WorkflowJobCollection';
import WorkflowRunCollection from 'js/Collections/WorkflowRunCollection';

/**
 * Workflow.
 */
export default class Workflow extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize
     *
     * @param {object} options Backbone.Model options object; 'options.connections' (ConnectionCollection or associated Backbone.Collection raw-object representation), 'options.workflow_input_ports' (InputPortCollection or associated Backbone.Collection raw-object representation), 'options.workflow_output_ports' (OutputPortCollection or associated Backbone.Collection raw-object representation), 'options.workflow_jobs' (WorkflowJobCollection or associated Backbone.Collection raw-object representation), and 'options.workflow_runs' (WorkflowRunCollection or associated Backbone.Collection raw-object representation) must also be provided
     */
    initialize(options)
    {
        this.set('connections', new ConnectionCollection(options.connections));
        this.set('workflow_input_ports', new InputPortCollection(options.workflow_input_ports));
        this.set('workflow_output_ports', new OutputPortCollection(options.workflow_output_ports));
        this.set('workflow_jobs', new WorkflowJobCollection(options.workflow_jobs));
        this.set('workflow_runs', new WorkflowRunCollection(options.workflow_runs));
    }

    /**
     * Returns defaults.
     *
     * @return {object} object holding default values
     */
    defaults()
    {
        return {description: null, name: null, created: null, updated: null, valid: false};
    }

    /**
     * Override of Backbone.Model.parse. This will populate 'workflow_runs', 'workflow_jobs', 'workflow_input_ports', and 'workflow_output_ports' with the appropriate models.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        const workflow_runs = new WorkflowRunCollection();
        if (response.workflow_runs) {
            for (const workflow_run of response.workflow_runs) {
                workflow_runs.add(workflow_run);
            }
        }

        const workflow_jobs = new WorkflowJobCollection();
        if (response.workflow_jobs) {
            for (const workflow_job of response.workflow_jobs) {
                workflow_jobs.add(workflow_job);
            }
        }

        const workflow_input_ports = new InputPortCollection();
        if (response.workflow_input_ports) {
            for (const workflow_input_port of response.workflow_input_ports) {
                workflow_input_ports.add(workflow_input_port);
            }
        }

        const workflow_output_ports = new OutputPortCollection();
        if (response.workflow_output_ports) {
            for (const workflow_output_port of response.workflow_output_ports) {
                workflow_output_ports.add(workflow_output_port);
            }
        }
        
        const parsed = {
            ...response,
            workflow_runs,
            workflow_jobs,
            workflow_input_ports,
            workflow_output_ports
        }

        return parsed;
    }
}
Workflow.prototype.routeName = 'workflows';