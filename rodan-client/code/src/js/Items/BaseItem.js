import $ from 'jquery';
import GUI_EVENTS from '../Shared/Events';
import paper from 'paper';
import Radio from 'backbone.radio';
import Rodan from 'rodan';

let itemMap = null;

/**
 * Base Item in WorkflowBuilder
 */
class BaseItem extends paper.Path
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC STATIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns associated item given a URL.
     */
    static getAssociatedItem(url)
    {
        if (!itemMap)
        {
            itemMap = {};
        }
        return itemMap[url];
    }

    /**
     * Associates given item with URL.
     */
    static associateItemWithUrl(item, url)
    {
        if (!itemMap)
        {
            itemMap = {};
        }
        itemMap[url] = item;
    }

    /**
     * Removes item from map with he provided URL.
     */
    static removeItemFromMap(url)
    {
        if (!itemMap)
        {
            itemMap = {};
        }
        if (itemMap[url])
        {
            delete itemMap[url];
        }
    }

    /**
     * Update all items.
     */
    static updateItems()
    {
        if (!itemMap)
        {
            itemMap = {};
        }
        for (var url in itemMap)
        {
            var item = itemMap[url];
            item.update();
        }
    }

    /**
     * Clears the map.
     */
    static clearMap()
    {
        itemMap = {};
    }

    /**
     * Returns context menu data for multiple items of this class.
     */
    static getContextMenuDataMultiple()
    {
        return [{channel: 'rodan-client_gui', label: 'Cancel', radiorequest: GUI_EVENTS.REQUEST__WORKFLOWBUILDER_GUI_HIDE_CONTEXTMENU}];
    }

///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor(options)
    {
        super(options.segments);
        this._initializeRadio(options);
        this._initializeAppearance(options);
        this._initializeModelBinding(options);
        this._initializeText(options);
        this._initializeInputEventHandlers(options);
    }

    /**
     * Returns associated model.
     */
    getModel()
    {
        return this._model;
    }

    /**
     * Returns context menu data for single item of this class.
     */
    getContextMenuDataSingle()
    {
        var menuItems = [];
        if (this.menuItems)
        {
            menuItems = this.menuItems;
        }
        return menuItems;
    }

    /**
     * Return true if this item can be moved by itself.
     */
    isMoveable()
    {
        return true;
    }

    /**
     * Moves the item.
     */
    move(delta)
    {
        this.position.x += delta.x;
        this.position.y += delta.y;
        if (this._text !== null)
        {
            this._text.position = this.bounds.center;
        }
        this._hasMoved = true;
    }

    /**
     * Set position.
     */
    setPosition(point)
    {
        this.position = point;
        if (this._text !== null)
        {
            this._text.position = this.bounds.center;
        }
        this._hasMoved = true;
    }

    /**
     * Set visibility.
     */
    setVisible(visible)
    {
        this.visible = visible;
        this._text.visible = this._useText && this.visible;
    }

    /**
     * Destroy.
     */
    destroy()
    {
        BaseItem.removeItemFromMap(this._modelURL);
        this._text.remove();
        this.remove();
    }

    /**
     * Updates the position to the server.
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
                var x = this.position.x / paper.view.zoom / paper.view.size.width;
                var y = this.position.y / paper.view.zoom / paper.view.size.height;
                var coordinates = {x: x, y: y};
                this._model.set({'appearance': coordinates});
                this._model.save(); 
                this._hasMoved = false;
            }
        }
    }

    /**
     * Gets coordinates from server.
     */
    loadCoordinates()
    {
        // Create callback.
        var callback = (coordinates) => this._handleCoordinateLoadSuccess(coordinates);

        // Fetch.
        var query = {};
        query[this.coordinateSetInfo['url']] = this._modelId;
        this._model.fetch({data: query, success: callback, error: callback});
    }

    /**
     * Returns associated model ID.
     */
    getModelID()
    {
        return this._modelId;
    }

    /**
     * Returns associated model URL.
     */
    getModelURL()
    {
        return this._modelURL;
    }

    /**
     * Highlights this object.
     */
    setHighlight(highlighted)
    {
        this.strokeColor = highlighted ? Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_COLOR_SELECTED : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_COLOR;
        this.strokeWidth = highlighted ? Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_WIDTH_SELECTED : Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_WIDTH;
    }

    /**
     * Gets description.
     */
    getDescription()
    {
        if (this._description && this._description !== '')
        {
            return this._description;
        }
        else
        {
            return 'no description available';
        }
    }

    /**
     * Sets temporary color.
     */
    setTemporaryColor(color)
    {
        this._temporaryColor = color;
    }

    /**
     * Clears temporary color.
     */
    clearTemporaryColor()
    {
        this._temporaryColor = null;
    }

///////////////////////////////////////////////////////////////////////////////////////
// ABSTRACT METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Abstract method. Update.
     */
    update()
    {
        // TODO - better way to do abstract methods
        console.error('This must be defined in sub-class.');
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Backbone event handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle event model sync.
     */
    _handleEventModelSync(options)
    {
        this._model = options.model;
        switch (options.options.task)
        {
            case 'save':
            {
                this._text.content = this._model.get('name');
                this._description = this._model.getDescription();
                break;
            }

            case 'destroy':
            {
                this.destroy();
                break;
            }

            default:
            {
                break;
            }
        }
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize hover.
     */
    _initializeHover(options)
    {
        this._timerEvent = null;
        this._popup = new paper.PointText(new paper.Point(0, 0));
    }

    /**
     * Initialize appearance.
     */
    _initializeAppearance(options)
    {
        this.strokeColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_COLOR;
        this.strokeJoin = 'round';
        this.strokeWidth = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_WIDTH;
        this.fillColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].FILL_COLOR;
        this._temporaryColor = null;
    }

    /**
     * Initialize model binding.
     */
    _initializeModelBinding(options)
    {
        this._model = options.model ? options.model: null;
        this._modelId = options.model ? options.model.id : null;
        this._modelURL = options.model ? options.model.get('url') : null;
        this._description = options.model ? options.model.getDescription() : null;
        BaseItem.associateItemWithUrl(this, this._modelURL);

        // This is the coordinate set model settings. Should be overridden if want to save.
        this._coordinateSetSaveAttempted = false;
    }

    /**
     * Initialize event handlers.
     */
    _initializeInputEventHandlers(options)
    {
        this.onMouseDown = event => this._handleMouseEvent(event);
        this.onMouseUp = event => this._handleMouseEvent(event);
        this.onClick = event => this._handleMouseEvent(event);
        this.onMouseEnter = event => this._handleMouseEvent(event);
        this.onMouseLeave = event => this._handleMouseEvent(event);
        this.onDoubleClick = event => this._handleMouseEvent(event);
        this._text.onMouseDown = event => this._handleMouseEvent(event);
        this._text.onMouseUp = event => this._handleMouseEvent(event);
        this._text.onClick = event => this._handleMouseEvent(event);
        this._text.onMouseEnter = event => this._handleMouseEvent(event);
        this._text.onMouseLeave = event => this._handleMouseEvent(event);
        this._text.onDoubleClick = event => this._handleMouseEvent(event);
    }

    /**
     * Initialize text.
     */
    _initializeText(options)
    {
        this._useText = (options.hasOwnProperty('text') && options.text === true);
        this._text = new paper.PointText(new paper.Point(0, 0));
        this._text.justification = 'center';
        this._text.fillColor = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].STROKE_COLOR;
        this._text.fontSize = Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].FONT_SIZE;
        this._text.content = '';
        this._text.position = this.bounds.center;
        this.addChild(this._text);
        if (options.model)
        {
            this._text.content = options.model.get('name');
        }
    }

    /**
     * Initialize radio.
     */
    _initializeRadio(options)
    {
        this.guiChannel = Radio.channel('rodan-client_gui');
        this.rodanChannel = Radio.channel('rodan');
        if (options && options.model)
        {
            this.rodanChannel.on(Rodan.RODAN_EVENTS.EVENT__MODEL_SYNC + options.model.get('url'), options => this._handleEventModelSync(options));
        }
    }

    /**
     * Handle coordinate load success.
     */
    _handleCoordinateLoadSuccess(model)
    {
        var coordinates = model.get("appearance");
        if (coordinates)
        {
            this.position = new paper.Point(coordinates.x * paper.view.size.width * paper.view.zoom, 
                                            coordinates.y * paper.view.size.height * paper.view.zoom);
        }
    }

    /**
     * Shows popup.
     */
    _showPopup(event)
    {
        if ($('div#canvas-tooltip'))
        {
            var description = this.getDescription();
            var tooltip = $('div#canvas-tooltip');
            tooltip.css('visibility', 'visible');
            tooltip.css('top', event.event.clientY);
            tooltip.css('left', event.event.clientX);
            tooltip.text(description);
        }
    }

    /**
     * Hide popup.
     */
    _hidePopup()
    {
        if ($('div#canvas-tooltip'))
        {
            $('div#canvas-tooltip').css('visibility', 'hidden');
        }
    }

    /**
     * Handle mouse event.
     */
    _handleMouseEvent(event)
    {
        // We do this because paperjs doesn't bubble up events.
        // This line guarantees that events caught by the TEXT actually get to the parent base item.
        event.target = this;

        switch (event.type)
        {
            case 'mouseenter':
            {
                this._timerEvent = setTimeout(() => this._showPopup(event), Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].HOVER_TIME);
                paper.handleMouseEvent(event);
                break;
            }

            case 'mouseleave':
            {
                this._hidePopup();
                clearTimeout(this._timerEvent);
                paper.handleMouseEvent(event);
                break;
            }

            case 'mouseup':
            {
                this._handleMouseUp(event);
                break;
            }

            case 'mousedown':
            {
                this._handleMouseDown(event);
                break;
            }

            case 'click':
            {
                this._handleClick(event);
                break;
            }

            case 'doubleclick':
            {
                this._handleDoubleClick(event);
                break;
            }

            default:
            {
                paper.handleMouseEvent(event);
                break;
            }
        }
    }

    /**
     * Handle mouse enter.
     */
    _handleMouseEnter(mouseEvent)
    {
        this._timerEvent = setTimeout(() => this._showPopup(mouseEvent), Rodan.Configuration.PLUGINS['rodan-client-wfbgui'].HOVER_TIME);
        paper.handleMouseEvent(mouseEvent);
    }

    /**
     * Handle mouse leave.
     */
    _handleMouseLeave(mouseEvent)
    {
        this._hidePopup();
        clearTimeout(this._timerEvent);
        paper.handleMouseEvent(mouseEvent); 
    }

    /**
     * Handle mouse up.
     */
    _handleMouseUp(mouseEvent)
    {
        paper.handleMouseEvent(mouseEvent);
    }

    /**
     * Handle mouse down.
     */
    _handleMouseDown(mouseEvent)
    {
        paper.handleMouseEvent(mouseEvent);
    }

    /**
     * Handle mouse click.
     */
    _handleClick(mouseEvent)
    {
        paper.handleMouseEvent(mouseEvent);
    }

    /**
     * Handle mouse double click.
     */
    _handleDoubleClick(mouseEvent)
    {
        paper.handleMouseEvent(mouseEvent);
    }
}

export default BaseItem;