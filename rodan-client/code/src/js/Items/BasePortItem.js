import BaseItem from './BaseItem';

/**
 * BasePortItem item.
 */
class BasePortItem extends BaseItem
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
        this._workflowJobUrl = options.workflowjoburl;
        this._ownerUrl = this._workflowJobUrl;
        this._ownerItem = null;
        this.onDoubleClick = event => this._handleDoubleClick(event);
    }

    /**
     * Return true if this item can be moved by itself.
     */
    isMoveable()
    {
        return false;
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        if (this._ownerItem)
        {
            this.removeFromOwner(this._ownerItem);
        }
        super.destroy();
    }

    /**
     * Return menu items.
     */
    getContextMenuDataSingle()
    {
        return this._menuItems;
    }

    /**
     * Returns associated WorkflowJobItem.
     */
    getWorkflowJobItem()
    {
        return BaseItem.getAssociatedItem(this._workflowJobUrl);
    }

    /**
     * Update.
     */
    update()
    {
        this.updateOwnership();
    }

    /**
     * Resets the owner to the WorkflowJobItem.
     */
    resetOwner()
    {
        this._ownerUrl = this._workflowJobUrl;
    }

    /**
     * Sets the owner URL.
     */
    setOwner(url)
    {
        this._ownerUrl = url;
    }

    /**
     * Updates ownership. It makes sure that the associated ownerItem (the one positioning it and setting the visibility) is set.
     * If it is NOT set, it looks for it. When found, it adds itself as a child.
     */
    updateOwnership()
    {
        this._ownerItem = BaseItem.getAssociatedItem(this._ownerUrl);
        if (this._ownerItem)
        {
            this.addToOwner(this._ownerItem);
        }
    }

    /**
     * Add this item to the owner.
     * Must be implemented by inheriting class.
     */
    addToOwner(ownerItem)
    {
        // TODO - better way to do abstract methods
        console.error('This must be defined in sub-class.');
    }

    /**
     * Remove this item from the owner.
     * Must be implemented by inheriting class.
     */
    removeFromOwner(ownerItem)
    {
        // TODO - better way to do abstract methods
        console.error('This must be defined in sub-class.');
    }
}

export default BasePortItem;