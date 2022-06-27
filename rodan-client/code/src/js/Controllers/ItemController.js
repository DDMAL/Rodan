import BaseItem from '../Items/BaseItem';
import ConnectionItem from '../Items/ConnectionItem';
import GUI_EVENTS from '../Shared/Events';
import InputPortItem from '../Items/InputPortItem';
import LineItem from '../Items/LineItem';
import OutputPortItem from '../Items/OutputPortItem';
import paper from 'paper';
import Radio from 'backbone.radio';
import Rodan from 'rodan';
import WorkflowJobGroupItem from '../Items/WorkflowJobGroupItem';
import WorkflowJobItem from '../Items/WorkflowJobItem';

/**
 * Controls management of items.
 */
class ItemController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Basic constructor
     */
    constructor()
    {
        this._selectedItems = {};
        this._selectingMultiple = false;
        this._overItem = null;
        this._outputPortItem = null;
        this._candidateInputPortItems = {};
        
        this._initializeRadio();
        this._createSegments();
    }

    /**
     * Handles MouseEvent on item.
     */
    handleMouseEvent(mouseEvent)
    {
        var item = mouseEvent.target;
        this._overItem = mouseEvent.type === 'mouseenter' ? item : mouseEvent.type === 'mouseleave' ? null : item;
        if (mouseEvent.type === 'mousedown')
        {
            this._handleEventMouseDown(mouseEvent);
        }
        else if (mouseEvent.type === 'mouseup')
        {
        }
    }

    /**
     * Returns current item mouse is over (or null).
     */
    getMouseOverItem()
    {
        return this._overItem;
    }

    /**
     * Saves item positions.
     */
    saveSelectedItemPositions()
    {
        for (var itemIndex in this._selectedItems)
        {
            var item = this._selectedItems[itemIndex];
            item.updatePositionToServer();
        } 
    }

    /**
     * Move item positions.
     */
    moveSelectedItems(delta)
    {
        for (var itemIndex in this._selectedItems)
        {
            var item = this._selectedItems[itemIndex];
            if (item.isMoveable())
            {
                item.move(delta); 
            }
        } 
    }

    /**
     * Selects the given item.
     */
    selectItem(item)
    {
        this._selectedItems[item.id] = item;
        item.setHighlight(true);
    }

    /**
     * Unselects the given item.
     */
    unselectItem(item)
    {
        delete this._selectedItems[item.id];
        item.setHighlight(false);
    }

    /**
     * Clears selection.
     */
    clearSelected()
    {
        for (var itemIndex in this._selectedItems)
        {
            var item = this._selectedItems[itemIndex];
            this.unselectItem(item);
        }
        this._selectedItems = {}; // TODO memory leak? 
        this._outputPortItem = null;
    }

    /**
     * Return true if item is selected.
     */
    isSelected(item)
    {
        return this._selectedItems.hasOwnProperty(item.id);
    }

    /**
     * Returns number of selected items.
     */
    getSelectedCount()
    {
        return Object.keys(this._selectedItems).length;
    }

    /**
     * Returns array of keys of selected items.
     */
    getSelectedItemKeys()
    {
        return Object.keys(this._selectedItems);
    }

    /**
     * Returns selected item at key
     */
    getSelectedItem(key)
    {
        return this._selectedItems[key];
    }

    /**
     * Returns true if we can group the selected items.
     */
    canGroupSelectedItems()
    {
        if (Object.keys(this._selectedItems).length > 1)
        {
            for (var itemIndex in this._selectedItems)
            {
                var item = this._selectedItems[itemIndex];
                if (!(item instanceof WorkflowJobItem))
                {
                    return false;
                }
            }
            return true;
        }
        return false;
    }

    /**
     * Return OutputPortItem flagged for Connection creation (null if none).
     */
    getOutputPortItemForConnection()
    {
        return this._outputPortItem;
    }

    /**
     * Returns a line item.
     */
    createLineItem(startPoint)
    {
        return new LineItem({segments: this._segments.connection, startPoint: startPoint});
    }

    /**
     * Set selecting multiple.
     */
    setSelectingMultiple(selectingMultiple)
    {
        this._selectingMultiple = selectingMultiple;
    }

    /**
     * Return true if selecting multiple.
     */
    selectingMultiple()
    {
        return this._selectingMultiple;
    }

    /**
     * Attempts to create a connection.
     */
    createConnection(outputPortItem, inputPortItem, workflow)
    {
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_ADD_CONNECTION, {inputport: inputPortItem.getModel(), 
                                                                                   outputport: outputPortItem.getModel(),
                                                                                   workflow: workflow});
    }

    /**
     * Given InputPort URLs, sets them as candidates for satisfying OutputPort.
     */
    setInputPortCandidates(inputPortUrls)
    {
        this.clearInputPortCandidates();
        if (inputPortUrls)
        {
            for (var i = 0; i < inputPortUrls.length; i++)
            {
                var item = BaseItem.getAssociatedItem(inputPortUrls[i]);
                item.setTemporaryColor(Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].INPUTPORT_COLOR_CANDIDATE);
                this._candidateInputPortItems[inputPortUrls[i]] = item;
            }
        }
    }

    /**
     * Returns true if provided InputPortItem represents a candidate InputPort.
     */
    isInputPortCandidate(item)
    {
        var url = item.getModel().get('url');
        return this._candidateInputPortItems.hasOwnProperty(url);
    }

    /**
     * Clears candidate InputPortItems.
     */
    clearInputPortCandidates()
    {
        var keys = Object.keys(this._candidateInputPortItems);
        for (var i = 0; i < keys.length; i++)
        {
            var item = this._candidateInputPortItems[keys[i]];
            item.clearTemporaryColor();
        }
        this._candidateInputPortItems = {};
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Initializers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize radio.
     */
    _initializeRadio()
    {
        this.guiChannel = Radio.channel('rodan-client_gui');
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_SELECTED_WORKFLOWJOBS, () => this._handleRequestGetSelectedWorkflowJobs());
        this.guiChannel.reply(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_ADD_RESOURCEDISTRIBUTOR, () => this._handleRequestAddResourceDistributor());

        this.rodanChannel = Radio.channel('rodan');
        this.rodanChannel.on(Rodan.RODAN_EVENTS.EVENT__COLLECTION_ADD, options => this._handleEventModelSync(options));
        this.rodanChannel.on(Rodan.RODAN_EVENTS.EVENT__MODEL_SYNC, options => this._handleEventModelSync(options));
    }

    /**
     * Create segment definitions.
     */
    _createSegments()
    {
        var canvasWidth = paper.view.viewSize.width;
        var canvasHeight = paper.view.viewSize.height;
        var workflowJobItemWidth = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].WORKFLOWJOB_WIDTH;
        var workflowJobItemHeight = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].WORKFLOWJOB_HEIGHT;
        var portItemWidth = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].PORT_WIDTH;
        var portItemHeight = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].PORT_HEIGHT;
        this._segments = {
            workflowJobItem: [
                new paper.Point(0, 0), 
                new paper.Point(workflowJobItemWidth, 0), 
                new paper.Point(workflowJobItemWidth, workflowJobItemHeight), 
                new paper.Point(0, workflowJobItemHeight), 
                new paper.Point(0, 0)
            ],
            portItem: [
                new paper.Point(0, 0), 
                new paper.Point(portItemWidth, 0), 
                new paper.Point(portItemWidth, portItemHeight), 
                new paper.Point(0, portItemHeight), 
                new paper.Point(0, 0)
            ],
            listInputportItem: [
                new paper.Point(0, 0), 
                new paper.Point(portItemWidth, 0), 
                new paper.Point(portItemWidth / 2, portItemHeight), 
                new paper.Point(0, 0)
            ],
            listOutputPortItem: [
                new paper.Point(portItemWidth / 2, 0), 
                new paper.Point(portItemWidth, portItemHeight), 
                new paper.Point(0, portItemHeight), 
                new paper.Point(portItemWidth / 2, 0)
            ],
            connection: [new paper.Point(0, 0), new paper.Point(1, 0)]
        };
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - REST handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event model sync.
     *
     * We check if an item exists for this model. If it does, don't do anything - the
     * model will take care of itself. If it doesn't, we create a new model.
     */
    _handleEventModelSync(options)
    {
        if (options.model)
        {
            var item = BaseItem.getAssociatedItem(options.model.get('url'));
            if (!item)
            {
                switch (options.model.constructor.name)
                {
                    case 'WorkflowJob':
                    {
                        var item = new WorkflowJobItem({segments: this._segments.workflowJobItem, model: options.model, text: true});
                        var position = new paper.Point(paper.view.size.width * paper.view.zoom / 2, paper.view.size.height * paper.view.zoom / 2);
                        item.setPosition(position);
                        break;
                    }

                    case 'InputPort':
                    {
                        var item = new InputPortItem({segments: this._segments.portItem, model: options.model, workflowjoburl: options.model.get('workflow_job')});
                        break;
                    }

                    case 'OutputPort':
                    {
                        var item = new OutputPortItem({segments: this._segments.portItem, model: options.model, workflowjoburl: options.model.get('workflow_job')});
                        break;
                    }

                    case 'Connection':
                    {
                        var item = new ConnectionItem({segments: this._segments.connection,
                                                       model: options.model, 
                                                       inputporturl: options.model.get('input_port'), 
                                                       outputporturl: options.model.get('output_port')});
                        break;
                    }

                    case 'WorkflowJobGroup':
                    {
                        var item = new WorkflowJobGroupItem({segments: this._segments.workflowJobItem, model: options.model, text: true});
                        var position = new paper.Point(paper.view.size.width * paper.view.zoom / 2, paper.view.size.height * paper.view.zoom / 2);
                        item.setPosition(position);
                        break;
                    }

                    default:
                    {
                        break;
                    }
                }
            }
            else if (options.options.task === 'destroy')
            {
                this.unselectItem(item);
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - MouseEvent handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event mousedown.
     */
    _handleEventMouseDown(mouseEvent)
    {
        // Handle selection first.
        var item = mouseEvent.target;
        if (!this._selectingMultiple)
        {
            if (!this.isSelected(item))
            {
                this.clearSelected();
                this.selectItem(item);
            } 
        }
        else
        {
            if (!this.isSelected(item))
            {
                this.selectItem(item);
            }
            else
            {
                this.unselectItem(item);
            }
        }

        // Next, what kind of button was it.
        switch (mouseEvent.event.button)
        {
            case 0:
            {
                this._handleEventMouseDownMain(mouseEvent);
                break;
            }

            default:
            {
                this._handleEventMouseDownSecondary(mouseEvent);
                break;
            }
        }
    }

    /**
     * Handle main button mousedown.
     */
    _handleEventMouseDownMain(mouseEvent)
    {
        // Check if we can start making a connection.
        var item = mouseEvent.target;
        if (this.getSelectedCount() === 1 && item instanceof OutputPortItem)
        {
            this._outputPortItem = item;
        } 
    }

    /**
     * Handle secondary button mousedown.
     */
    _handleEventMouseDownSecondary(mouseEvent)
    {
        var itemClass = this._getSelectionItemType();
        var contextMenuData = [];
        if (this.getSelectedCount() === 1)
        {
            var item = mouseEvent.target;
            contextMenuData = item.getContextMenuDataSingle();
        }
        else
        {
            contextMenuData = itemClass.getContextMenuDataMultiple();
        }

        if (contextMenuData && contextMenuData.length > 0)
        {
            Radio.channel('rodan').request(Rodan.RODAN_EVENTS.REQUEST__CONTEXTMENU_SHOW, {items: contextMenuData, 
                                                                                    top: mouseEvent.event.pageY,
                                                                                    left: mouseEvent.event.pageX});
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle request for all selected WorkflowJobs.
     */
    _handleRequestGetSelectedWorkflowJobs()
    {
        var workflowJobs = [];
        for (var itemIndex in this._selectedItems)
        {
            workflowJobs.push(this._selectedItems[itemIndex].getModel());
        }
        return workflowJobs;
    }

    /**
     * Handle add resource distributor for selected InputPorts.
     */
    _handleRequestAddResourceDistributor(options)
    {
        var keys = this.getSelectedItemKeys();
        var inputPorts = [];
        for (var index in keys)
        {
            var item = this.getSelectedItem(keys[index]);
            inputPorts.push(item.getModel());
        }
        var workflow = this.guiChannel.request(GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW);
        this.rodanChannel.request(Rodan.RODAN_EVENTS.REQUEST__WORKFLOWBUILDER_ADD_DISTRIBUTOR, {inputports: inputPorts, workflow: workflow});
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns item type (class constructor) of multiple selection.
     * If mixed, returns BaseItem. Returns null if none.
     */
    _getSelectionItemType()
    {
        var keys = this.getSelectedItemKeys();
        var itemType = null;
        var urls = [];
        for (var index in keys)
        {
            var item = this.getSelectedItem(keys[index]);
            if (itemType === null)
            {
                itemType = item.constructor;
            }
        }
        return itemType;
    }
}

export default ItemController;