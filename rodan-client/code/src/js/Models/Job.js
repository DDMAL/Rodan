import BaseModel from './BaseModel';
import InputPortTypeCollection from 'js/Collections/InputPortTypeCollection';
import OutputPortTypeCollection from 'js/Collections/OutputPortTypeCollection';

/**
 * Job.
 */
export default class Job extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the model. Upon initialization the 'input_port_types' and 'output_port_types' will be set as Backbone.Collections.
     *
     * @param {object} options Backbone.Model options object; 'options.input_port_types' and 'options.output_port_types' may be given
     */
    initialize(options)
    {
        this.set('input_port_types', new InputPortTypeCollection(options.input_port_types));
        this.set('output_port_types', new OutputPortTypeCollection(options.output_port_types));
    }

    /**
     * Override of Backbone.Model.defaults. Sets 'input_port_types' and 'output_port_types' to null.
     *
     * @todo is this needed?
     * @return {object} default properties
     */ 
    defaults()
    {
        return {input_port_types: null, output_port_types: null};
    }

    /**
     * Override of Backbone.Model.parse. The 'input_port_types' and 'output_port_types' will be set as Backbone.Collections.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     */
    parse(response)
    {
        response.input_port_types = new InputPortTypeCollection(response.input_port_types);
        response.output_port_types = new OutputPortTypeCollection(response.output_port_types);
        return response;
    }
}
Job.prototype.routeName = 'jobs';