import BaseItem from './BaseItem';
import paper from 'paper';

/**
 * BaseWorkflowJob item. 
 */
class BaseWorkflowJobItem extends BaseItem
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
        this._paperGroupInputPorts = new paper.Group();
        this.addChild(this._paperGroupInputPorts);
        this._paperGroupOutputPorts = new paper.Group();
        this.addChild(this._paperGroupOutputPorts);
        this.onDoubleClick = event => this._handleDoubleClick(event);
    }

    /**
     * Update.
     */
    update()
    {
        if (this.visible)
        {
            this.bounds.width = this._text.bounds.width + 10;
            this._text.position = this.bounds.center;
            this._paperGroupInputPorts.position = this.bounds.topCenter;
            this._paperGroupOutputPorts.position = this.bounds.bottomCenter;
            this._positionPortItems(this._paperGroupInputPorts, this.bounds.top);
            this._positionPortItems(this._paperGroupOutputPorts, this.bounds.bottom);
        }
        this._updatePortItemVisibility(this._paperGroupInputPorts);
        this._updatePortItemVisibility(this._paperGroupOutputPorts);
    }

    /**
     * Adds input port item.
     */
    addInputPortItem(inputPortItem)
    {
        this._paperGroupInputPorts.addChild(inputPortItem);
    }

    /**
     * Adds output port item.
     */
    addOutputPortItem(outputPortItem)
    {
        this._paperGroupOutputPorts.addChild(outputPortItem);
    }

    /**
     * Deletes input port item.
     */
    deleteInputPortItem(inputPortItem)
    {
        this._deletePortItem(this._paperGroupInputPorts, inputPortItem);
    }

    /**
     * Deletes output port item.
     */
    deleteOutputPortItem(outputPortItem)
    {
        this._deletePortItem(this._paperGroupOutputPorts, outputPortItem);
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        super.destroy();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Positions ports.
     */
    _positionPortItems(group, positionY)
    {
        if (group.isEmpty())
        {
            return;
        }

        // Get port width and height.
        var portWidth = group.children[0].bounds.width;
        var portHeight = group.children[0].bounds.height;
        var groupWidth = group.children.length * portWidth;

        // Get position parameters.
        var offsetX = group.children[0].bounds.width;
        var farLeft = this.position.x - (groupWidth / 2);

        for (var i = 0; i < group.children.length; i++)
        {
            var port = group.children[i];
            var positionX = (farLeft + (offsetX * (i + 1))) - (group.children[i].bounds.width / 2);
            var newPosition = new paper.Point(positionX, positionY);
            port.position = newPosition;
        }
    }

    /**
     * Updates port item visibility.
     */
    _updatePortItemVisibility(group)
    {
        for (var i = 0; i < group.children.length; i++)
        {
            var port = group.children[i];
            group.children[i].setVisible(this.visible);
        }
    }

    /**
     * Deletes a port item.
     */
    _deletePortItem(group, portItem)
    {
        for (var i = 0; i < group.children.length; i++)
        {
            if (portItem === group.children[i])
            {
                group.removeChildren(i, i + 1);
                return;
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle double click.
     */
    _handleDoubleClick(mouseEvent)
    {
        // TODO - better way to do abstract methods
        console.error('This must be defined in sub-class.');
    }
}

export default BaseWorkflowJobItem;