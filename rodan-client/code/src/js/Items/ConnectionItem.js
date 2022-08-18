import paper from 'paper';
import BaseItem from './BaseItem';
import GUI_EVENTS from '../Shared/Events';
import Rodan from 'rodan';

/**
 * Connection item.
 */
class ConnectionItem extends BaseItem
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

        var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.menuItems = [{label: 'Delete', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_REMOVE_CONNECTION, options: {connection: options.model, workflow: workflow}}];

        this.strokeWidth = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_WIDTH;
        this._inputPortItem = null;
        this._outputPortItem = null;
        this._inputPortUrl = options.inputporturl;
        this._outputPortUrl = options.outputporturl;

        // We'll put a small circle in the middle of our connection so it's easier to select.
        var circleCenter = new paper.Point(0, 0);
        this._circle = new paper.Shape.Circle(circleCenter, Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].CONNECTION_CIRCLE_RADIUS);
        this._circle.fillColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_COLOR;
        this._circle.onMouseDown = event => this._handleMouseEvent(event);
        this._circle.onMouseUp = event => this._handleMouseEvent(event);
        this._circle.onClick = event => this._handleMouseEvent(event);
        this._circle.onMouseEnter = event => this._handleMouseEvent(event);
        this._circle.onMouseLeave = event => this._handleMouseEvent(event);
        this.addChild(this._circle);
    }

    /**
     * Return true if this item can be moved by itself.
     */
    isMoveable()
    {
        return false;
    }

    /**
     * Update.
     */
    update()
    {
        // We do this in case the InputPortItem was created AFTER this ConnectionItem.
        if (!this._inputPortItem)
        {
            this._inputPortItem = BaseItem.getAssociatedItem(this._inputPortUrl);
            if (this._inputPortItem)
            {
                this._inputPortItem.setConnectionItem(this);
            }
        }

        // We do this in case the OutputPortItem was created AFTER this port.
        if (!this._outputPortItem)
        {
            this._outputPortItem = BaseItem.getAssociatedItem(this._outputPortUrl);
            if (this._outputPortItem)
            {
                this._outputPortItem.addConnectionItem(this);
            }
        }

        if (this._inputPortItem && this._outputPortItem)
        {
            this._circle.visible = this.visible;
            this.firstSegment.point.x = this._outputPortItem.position.x;
            this.firstSegment.point.y = this._outputPortItem.bounds.bottom;
            this.lastSegment.point.x = this._inputPortItem.position.x;
            this.lastSegment.point.y = this._inputPortItem.bounds.top;
            this._circle.position.x = this.firstSegment.point.x + ((this.lastSegment.point.x - this.firstSegment.point.x) / 2);
            this._circle.position.y = this.firstSegment.point.y + ((this.lastSegment.point.y - this.firstSegment.point.y) / 2);
        }
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        this._circle.remove();
        if (this._inputPortItem)
        {
            this._inputPortItem.setConnectionItem(null);
        }
        this._inputPortItem = null;
        if (this._outputPortItem)
        {
            this._outputPortItem.removeConnectionItem(this);
        }
        this._outputPortItem = null;
        super.destroy();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
}

export default ConnectionItem;