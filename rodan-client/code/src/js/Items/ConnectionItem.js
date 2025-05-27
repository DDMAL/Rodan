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
        this._padding = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].CONNECTION_PADDING;
        this._offsetX = this._model.get('offset_x');
        this._offsetY = this._model.get('offset_y');
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

            this.removeSegments();

            // If the input port is above the output port, we want to draw the connection in a different way using 5 line segments instead of 3.
            if (this._inputPortItem.bounds.top < this._outputPortItem.bounds.bottom + 2 * this._padding) {
                if (this._offsetX == null) {
                    this._circle.position.x = (this._inputPortItem.position.x + this._outputPortItem.position.x) / 2;
                } else {
                    this._circle.position.x = this._outputPortItem.position.x + this._offsetX;
                }
                
                this._circle.position.y = (this._inputPortItem.position.y + this._outputPortItem.position.y) / 2;

                const start = new Point(this._outputPortItem.position.x, this._outputPortItem.bounds.bottom);
                const p1 = new Point(this._outputPortItem.position.x, this._outputPortItem.bounds.bottom + this._padding);
                const p2 = new Point(this._circle.position.x, this._outputPortItem.bounds.bottom + this._padding);
                const p3 = new Point(this._circle.position.x, this._inputPortItem.bounds.top - 5);
                const p4 = new Point(this._inputPortItem.position.x, this._inputPortItem.bounds.top - 5);
                const end = new Point(this._inputPortItem.position.x, this._inputPortItem.bounds.top);

                this.add(start, p1, p2, p3, p4, end);
            } else {
                if (this._offsetY == null) {
                    this._circle.position.y = (this._inputPortItem.bounds.top + this._outputPortItem.bounds.bottom) / 2;
                } else {
                    this._circle.position.y = this._clamp(this._outputPortItem.bounds.bottom + this._offsetY, this._outputPortItem.bounds.bottom + this._padding, this._inputPortItem.bounds.top - 5);
                }
                
                this._circle.position.x = (this._inputPortItem.position.x + this._outputPortItem.position.x) / 2;

                const start = new Point(this._inputPortItem.position.x, this._inputPortItem.bounds.top);
                const p1 = new Point(this._inputPortItem.position.x, this._circle.position.y);
                const p2 = new Point(this._outputPortItem.position.x, this._circle.position.y);
                const end = new Point(this._outputPortItem.position.x, this._outputPortItem.bounds.bottom);
    
                this.add(start, p1, p2, end);
            }
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
     * Overrides move method to calculate and update offset instead of position.
     */
    move(delta)
    {
        if (this._inputPortItem.bounds.top < this._outputPortItem.bounds.bottom + 2 * this._padding) {
            this._offsetX = (this._circle.position.x - this._outputPortItem.position.x) + delta.x;
        } else {
            this._offsetY = (this._circle.position.y - this._outputPortItem.bounds.bottom) + delta.y;
        }
        this._hasMoved = true;
    }

    /**
     * Overrides updatePositionToServer to update offset instead of position.
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
                this._model.set({ offset_x: this._offsetX, offset_y: this._offsetY });
                this._model.save();
                this._hasMoved = false;
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
   /**
    * Clamps a value between a min and max.
    */
    _clamp(value, min, max)
        {
            return Math.min(Math.max(value, min), max);
        }
    }

export default ConnectionItem;