import BaseModel from './BaseModel';

/**
 * Project model.
 */
export default class Project extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Override of Backbone.Model.parse. This sets the 'workflow_count' if not provided by the server.
     *
     * @param {object} response JSON response from server
     * @return {object} response object
     * @todo why is it not being provided by the server?
     */
    parse(response)
    {
        response = super.parse(response);
        if (!response.hasOwnProperty('workflow_count'))
        {
            response.workflow_count = response.workflows.length;
        }
        return response;
    }

    /**
     * Return defaults.
     *
     * @return {object} default properties
     */
    defaults()
    {
        return {creator: {username: null},
                created: null,
                updated: null,
                workflow_count: null,
                resource_count: null,
                name: 'untitled'};
    }
}
Project.prototype.routeName = 'projects';