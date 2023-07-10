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
        this.fillColor = null;
        this._startPoint = options.startPoint;
    }

    /**
     * Sets endpoint.
     */
    setEndPoint(endpoint)
    {
        this.removeSegments();
        const mid1 = new Point(this._startPoint.x, (this._startPoint.y + endpoint.y) / 2);
        const mid2 = new Point(endpoint.x, (this._startPoint.y + endpoint.y) / 2);
        this.add(this._startPoint, mid1, mid2, endpoint);
    }

    /**
     * Update (dummy).
     */
    update()
    {}
}

export default LineItem;