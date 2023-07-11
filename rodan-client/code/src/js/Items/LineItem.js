import BaseItem from './BaseItem';
import Rodan from 'rodan';

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
        this._padding = this._padding = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].CONNECTION_PADDING;
    }

    /**
     * Sets endpoint.
     */
    setEndPoint(endpoint)
    {
        this.removeSegments();

        if (this._startPoint.y + 2 * this._padding > endpoint.y) {
            const p1 = new Point(this._startPoint.x, this._startPoint.y + this._padding);
            const p2 = new Point((this._startPoint.x + endpoint.x) / 2, this._startPoint.y + this._padding);
            const p3 = new Point((this._startPoint.x + endpoint.x) / 2, endpoint.y - this._padding);
            const p4 = new Point(endpoint.x, endpoint.y - 5);
            this.add(this._startPoint, p1, p2, p3, p4, endpoint);
        } else {
            const p1 = new Point(this._startPoint.x, (this._startPoint.y + endpoint.y) / 2);
            const p2 = new Point(endpoint.x, (this._startPoint.y + endpoint.y) / 2);
            this.add(this._startPoint, p1, p2, endpoint);
        }
    }

    /**
     * Update (dummy).
     */
    update()
    {}
}

export default LineItem;