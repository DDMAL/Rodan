import BaseModel from './BaseModel';

/**
 * Pagination. Note that this has no 'routeName' since pagination is stored within a Collection. This model is simply here for convenience.
 */
export default class Pagination extends BaseModel
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Set defaults.
     *
     * @return {object} default properties
     */
    defaults()
    {
        return {count: 0, next: '#', previous: '#', current: 1, total: 1};
    }
}
Pagination.prototype.routeName = null;