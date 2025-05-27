import BasePortItem from './BasePortItem';
import Rodan from 'rodan';

/**
 * OutputPort item.
 */
class OutputPortItem extends BasePortItem
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
        this.fillColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].OUTPUTPORT_COLOR;
        this._connectionItems = [];
    }

    /**
     * Adds associated connection item.
     */
    addConnectionItem(item)
    {
        this._connectionItems.push(item);
    }

    /**
     * Removes connection item.
     */
    removeConnectionItem(item)
    {
        for (var i = 0; i < this._connectionItems.length; i++)
        {
            if (this._connectionItems[i] === item)
            {
                this._connectionItems.splice(i, 1);
            }
        }
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        this._destroyConnections();
        super.destroy();
    }

    /**
     * Override.
     */
    addToOwner(ownerItem)
    {
        ownerItem.addOutputPortItem(this);
    }

    /**
     * Override.
     */
    removeFromOwner(ownerItem)
    {
        ownerItem.deleteOutputPortItem(this);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Destroys connections.
     */
    _destroyConnections()
    {
        while (this._connectionItems.length > 0)
        {
            this._connectionItems[0].destroy();
        } 
        this._connectionItems = [];
    }

    /**
     * Handle click.
     */
    _handleClick(event)
    {
        super._handleClick(event);
    }
}

export default OutputPortItem;