import paper from 'paper';
import BaseItem from './BaseItem';
import GUI_EVENTS from '../Shared/Events';
import Rodan from 'rodan';
import { Segment } from 'paper';

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
        this.fillColor = null;
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
        this._ratio = this._model.get('ratio');
    }

    /**
     * Return true if this item can be moved by itself.
     */
    isMoveable()
    {
        return true;
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
            this._circle.position.x = (this._inputPortItem.position.x + this._outputPortItem.position.x) / 2;
            this._circle.position.y = this._outputPortItem.bounds.bottom + (this._inputPortItem.bounds.top - this._outputPortItem.bounds.bottom) * this._ratio;

            this.removeSegments();

            const start = new Point(this._inputPortItem.position.x, this._inputPortItem.bounds.top);
            const mid1 = new Point(this._inputPortItem.position.x, this._circle.position.y);
            const mid2 = new Point(this._outputPortItem.position.x, this._circle.position.y);
            const end = new Point(this._outputPortItem.position.x, this._outputPortItem.bounds.bottom);

            this.add(start, mid1, mid2, end);
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

    /**
     * Overrides move method to calculate and update ratio instead of position.
     */
    move(delta)
    {
        const y = this._circle.position.y + delta.y;
        this._ratio = (y - this._outputPortItem.bounds.bottom) / (this._inputPortItem.bounds.top - this._outputPortItem.bounds.bottom);
        this._hasMoved = true;
    }

    /**
     * Overrides updatePositionToServer to update ratio instead of position.
     */
    updatePositionToServer()
    {
        if (this.isMoveable() && this._hasMoved)
        {
            // If an ID exists, we know it exists on the server, so we can patch it.
            // Else if we haven't tried saving it before, do it. This should create
            // a new model on the server.
            if (this._modelId || !this._coordinateSetSaveAttempted)
            {
                this._coordinateSetSaveAttempted = true;
                this._model.set({ ratio: this._ratio });
                this._model.save();
                this._hasMoved = false;
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
}

export default ConnectionItem;