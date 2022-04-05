import Marionette from 'backbone.marionette';

/**
 * Base controller.
 */
export default class BaseController extends Marionette.Object
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     *
     * @param {object} options Marionette.Object options object
     */
    constructor(options)
    {
        super(options);
        this._initializeViews();
        this._initializeRadio();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
    }

    /**
     * Initialize views.
     */
    _initializeViews()
    {
    }
}