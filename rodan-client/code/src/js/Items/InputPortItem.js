import BasePortItem from './BasePortItem';
import GUI_EVENTS from '../Shared/Events';
import Rodan from 'rodan';

/**
 * InputPort item.
 */
class InputPortItem extends BasePortItem
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC STATIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns context menu data for multiple items of this class.
     * Takes in URLs of multiple selections.
     *
     * The menu data is simply an array of objects. Objects should be:
     *
     * {
     *      label: [string] // The text that should appear
     *      radiorequest: Rodan.RODAN_EVENTS.?  // The Request to make. NOT A RADIO EVENT, rather a REQUEST.
     *      options: Object holding any options for Event
     * }
     */
    static getContextMenuDataMultiple()
    {
        return [{channel: 'rodan-client_gui', label: 'Create Resource Distributor', radiorequest: GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ADD_RESOURCEDISTRIBUTOR}];
    }

///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        super(options);
        this._connectionItem = null;
    }

    /**
     * Sets associated connection item.
     */
    setConnectionItem(item)
    {
        this._connectionItem = item;
    }

    /**
     * Return true if has connection item.
     */
    hasConnectionItem()
    {
        return this._connectionItem !== null;
    }

    /**
     * Return true if satisfied.
     */
    isSatisfied()
    {
        var resourceAssignments = this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_GET_RESOURCEASSIGNMENTS, {inputport: this.getModel()});
        return this.hasConnectionItem() || resourceAssignments.length > 0;
    }

    /**
     * Update.
     */
    update()
    {
        super.update();
        if (this._temporaryColor)
        {
            this.fillColor = this._temporaryColor;
        }
        else
        {
            this.fillColor = this.isSatisfied() ? Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].INPUTPORT_COLOR_SATISFIED : 
                                                  Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].INPUTPORT_COLOR_UNSATISFIED;
        }
        if (this._connectionItem !== null)
        {
            this._connectionItem.setVisible(this.visible);
        }
    }

    /**
     * Destroy cleanup.
     */
    destroy()
    {
        if (this.hasConnectionItem())
        {
            this._connectionItem.destroy();
            this._connectionItem = null;
        }
        super.destroy();
    }

    /**
     * Returns context menu data for single item of this class.
     * We override as some things should not be visible.
     */
    getContextMenuDataSingle()
    {
        var menuItems = [];
        if (!this.hasConnectionItem())
        {
            var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
            menuItems.push({label: 'Assign Resources', radiorequest: Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_RESOURCEASSIGNMENT_VIEW, options: {inputport: this.getModel(), workflow: workflow}});
        }
        return menuItems;
    }

    /**
     * Override.
     */
    addToOwner(ownerItem)
    {
        ownerItem.addInputPortItem(this);
    }

    /**
     * Override.
     */
    removeFromOwner(ownerItem)
    {
        ownerItem.deleteInputPortItem(this);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle double click.
     */
    _handleDoubleClick(mouseEvent)
    {
        if (!this.hasConnectionItem())
        {
            var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
            this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_SHOW_RESOURCEASSIGNMENT_VIEW, {inputport: this.getModel(), workflow: workflow});
        }
    }
}

export default InputPortItem;