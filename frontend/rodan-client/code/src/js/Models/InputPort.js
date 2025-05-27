import BaseModel from './BaseModel';

/**
 * InputPort.
 */
export default class InputPort extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Override of Backbone.Model.defaults. Sets default label to null.
     *
     * @return {object} defaults
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
InputPort.prototype.routeName = 'inputports';