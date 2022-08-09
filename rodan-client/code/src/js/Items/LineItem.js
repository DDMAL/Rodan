import BaseItem from './BaseItem';

/**
 * Line item.
 */
class LineItem extends BaseItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        super(options);
        this.firstSegment.point = options.startPoint;
    }

    /**
     * Sets endpoint.
     */
    setEndPoint(point)
    {
        this.lastSegment.point = point;
    }

    /**
     * Update (dummy).
     */
    update()
    {}
}

export default LineItem;