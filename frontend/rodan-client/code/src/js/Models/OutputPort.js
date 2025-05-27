import BaseModel from './BaseModel';

/**
 * InputPort.
 */
export default class OutputPort extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Override of Backbone.Model.defaults. Sets default label to null.
     *
     * @return {object} default properties
     */ 
    defaults()
    {
        return {label: null};
    }

    /**
     * Returns human-readable descriptive text.
     *
     * @return {string} 'label' property
     */
    getDescription()
    {
        return this.get('label');
    }
}
OutputPort.prototype.routeName = 'outputports';