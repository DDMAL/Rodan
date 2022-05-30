/*jshint esversion: 6 */
/**
 * This plugin will be used to transform Diva into a layering tool which will be used to provide
 * the ground truth data for the machine learning algorithm
 * that classifies and isolates the different components of old manuscripts and scores.
 *
 * {string} pluginName - Added to the class prototype. Defines the name for the plugin.
 *
 **/

import {Point} from './point';
import {Rectangle} from './rectangle';
import {Layer} from './layer';
import {Colour} from './colour';
import {Export} from './export';
import {UIManager} from './ui-manager';
import {Tools} from './tools';
import {Import} from './import';
import {Selection} from './selection';
import {Tutorial} from './tutorial';
import
{
    CannotDeleteLayerException,
    CannotSelectLayerException
} from "./exceptions";


export default class PixelPlugin
{
    constructor (core)
    {
        this.core = core;
        this.activated = false;
        this.pageToolsIcon = this.createIcon();
        this.scrollEventHandle = null;
        this.zoomEventHandle = null;
        this.mouseHandles = null;
        this.keyboardHandles = null;
        this.background = null;
        this.layers = null;
        this.mousePressed = false;
        this.rightMousePressed = false;
        this.selectedLayerIndex = 0;
        this.layerChangedMidDraw = false;
        this.actions = [];
        this.undoneActions = [];
        this.shiftDown = false;
        this.initialShiftPress = true;
        this.lastRelCoordX = null;
        this.lastRelCoordY = null;
        this.uiManager = null;
        this.tools = null;
        this.selection = null;
        this.horizontalMove = false;
        this.layerIdCounter = 2;
    }

    /**
     * ===============================================
     *         Plugin Activation/Deactivation
     * ===============================================
     **/

    handleClick ()
    {
        if (!this.activated)
            this.activatePlugin();
        else
            this.deactivatePlugin();
    }

    activatePlugin ()
    {
        if (this.layers === null)
        {
            // Start by creating layers
            let background = new Layer(0, new Colour(242, 242, 242, 1), "Background", this, 1),
                layer1 = new Layer(1, new Colour(51, 102, 255, 1), "Layer 1", this, 0.5);

            this.layers = [layer1];
            this.background = background;
            this.background.canvas = this.core.getSettings().renderer._canvas;  // Link background canvas to the actual diva canvas
        }

        if (this.uiManager === null)
            this.uiManager = new UIManager(this);

        if (this.tools === null)
            this.tools = new Tools(this);

        this.uiManager.createPluginElements(this.layers);
        this.scrollEventHandle = this.subscribeToScrollEvent();
        this.zoomEventHandle = this.subscribeToZoomLevelWillChangeEvent();

        this.disableDragScrollable();
        this.subscribeToWindowResizeEvent();
        this.subscribeToMouseEvents();
        this.subscribeToKeyboardEvents();

        // Setting Tool to change the cursor type
        this.tools.setCurrentTool(this.tools.getCurrentTool());
        this.activated = true;

        new Tutorial();
    }

    deactivatePlugin ()
    {
        global.Diva.Events.unsubscribe(this.scrollEventHandle);
        global.Diva.Events.unsubscribe(this.zoomEventHandle);

        this.unsubscribeFromMouseEvents();
        this.unsubscribeFromKeyboardEvents();
        this.redrawAllLayers(); // Repaint the tiles to make the highlights disappear off the page

        this.uiManager.destroyPluginElements(this.layers, this.background);
        this.enableDragScrollable();
        this.activated = false;
    }

    enableDragScrollable ()
    {
        if (this.core.viewerState.viewportObject.hasAttribute('nochilddrag'))
            this.core.viewerState.viewportObject.removeAttribute('nochilddrag');
    }

    disableDragScrollable ()
    {
        if (!this.core.viewerState.viewportObject.hasAttribute('nochilddrag'))
            this.core.viewerState.viewportObject.setAttribute('nochilddrag', "");
    }

    createIcon ()
    {
        const pageToolsIcon = document.createElement('div');
        pageToolsIcon.classList.add('diva-pixel-icon');

        let root = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        root.setAttribute("x", "0px");
        root.setAttribute("y", "0px");
        root.setAttribute("viewBox", "0 0 25 25");
        root.id = `${this.core.settings.selector}pixel-icon`;

        let g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.id = `${this.core.settings.selector}pixel-icon-glyph`;
        g.setAttribute("transform", "matrix(1, 0, 0, 1, -11.5, -11.5)");
        g.setAttribute("class", "diva-pagetool-icon");

        //Placeholder icon
        let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute('x', '15');
        rect.setAttribute('y', '10');
        rect.setAttribute('width', '25');
        rect.setAttribute('height', '25');

        g.appendChild(rect);
        root.appendChild(g);

        pageToolsIcon.appendChild(root);

        return pageToolsIcon;
    }

    /**
     * ===============================================
     *        Event Subscription/Unsubscription
     * ===============================================
     **/

    // Repositions all layers on top of editing page when the browser window is resized
    subscribeToWindowResizeEvent ()
    {
        window.addEventListener("resize", () =>
        {
            this.layers.forEach ((layer) =>
            {
                layer.placeLayerCanvasOnTopOfEditingPage();
            });
        });
    }

    // Resizes the elements of the layers on viewport zoom
    subscribeToZoomLevelWillChangeEvent ()
    {
        let handle = global.Diva.Events.subscribe('ZoomLevelWillChange', (zoomLevel) =>
        {
            this.layers.forEach ((layer) =>
            {
                layer.resizeLayerCanvasToZoomLevel(zoomLevel);
            });
        });
        return handle;
    }

    // Repositions all layers on top of editing page on viewport scroll
    subscribeToScrollEvent ()
    {
        let handle = global.Diva.Events.subscribe('ViewerDidScroll', () =>
        {
            this.layers.forEach ((layer) =>
            {
                layer.placeLayerCanvasOnTopOfEditingPage();
            });
        });
        return handle;
    }

    subscribeToMouseEvents ()
    {
        let canvas = document.getElementById("diva-1-outer");
        this.uiManager.createBrushCursor();

        this.mouseDown = (evt) => { this.onMouseDown(evt); };
        this.mouseUp = (evt) => { this.onMouseUp(evt); };
        this.mouseMove = (evt) => { this.onMouseMove(evt); };

        canvas.addEventListener('mousedown', this.mouseDown);
        canvas.addEventListener('mouseup', this.mouseUp);
        canvas.addEventListener('mouseleave', this.mouseUp);
        canvas.addEventListener('mousemove', this.mouseMove);

        // Used for unsubscription
        this.mouseHandles = {
            mouseDownHandle: this.mouseDown,
            mouseMoveHandle: this.mouseMove,
            mouseUpHandle: this.mouseUp
        };
    }

    subscribeToKeyboardEvents ()
    {
        this.handleKeyUp = (e) => { this.onKeyUp(e); };
        this.handleKeyDown = (e) => { this.onKeyDown(e); };

        document.addEventListener("keyup", this.handleKeyUp);
        document.addEventListener("keydown", this.handleKeyDown);

        // Used for unsubscription
        this.keyboardHandles = {
            keyup: this.handleKeyUp,
            keydown: this.handleKeyDown
        };
    }

    unsubscribeFromMouseEvents ()
    {
        let canvas = document.getElementById("diva-1-outer");

        canvas.removeEventListener('mousedown', this.mouseHandles.mouseDownHandle);
        canvas.removeEventListener('mouseup', this.mouseHandles.mouseUpHandle);
        canvas.removeEventListener('mouseleave', this.mouseHandles.mouseUpHandle);
        canvas.removeEventListener('mousemove', this.mouseHandles.mouseMoveHandle);
    }

    unsubscribeFromKeyboardEvents ()
    {
        document.removeEventListener("keyup", this.keyboardHandles.keyup);
        document.removeEventListener("keydown", this.keyboardHandles.keydown);
    }

    /**
     * ===============================================
     *        Handling Keyboard and Mouse Events
     * ===============================================
     *         Layer reordering (Drag and Drop)
     * -----------------------------------------------
     **/

    // Determines which element is being picked up
    dragStart (event)
    {
        event.dataTransfer.setData("Text", event.target.id);
    }

    dragging () //can take an event as an argument
    {
        // Do nothing
    }

    // Mark area as a drop zone on hover
    allowDrop (event)
    {
        event.preventDefault();
    }

    drop (event, departureLayerIndex, destinationLayerIndex)
    {
        event.preventDefault();
        this.reorderLayers(departureLayerIndex, destinationLayerIndex);
    }

    reorderLayers (departureLayerIndex, destinationLayerIndex)
    {
        let tempLayerStorage = this.layers[departureLayerIndex];

        if (departureLayerIndex > destinationLayerIndex)
        {
            for (let i = 1; i <= (departureLayerIndex - destinationLayerIndex); i++)
            {
                this.layers[departureLayerIndex - i + 1] = this.layers[departureLayerIndex - i];
            }
            this.layers[destinationLayerIndex] = tempLayerStorage;
        }

        else if (departureLayerIndex < destinationLayerIndex)
        {
            for (let i = 1; i <= (destinationLayerIndex - departureLayerIndex); i++)
            {
                this.layers[departureLayerIndex - 1 + i] = this.layers[parseFloat(departureLayerIndex) + i];
            }
            this.layers[destinationLayerIndex] = tempLayerStorage;
        }

        // Destroy all UI elements then recreate them (to show that the layers have been reordered through the UI)
        this.changeCurrentlySelectedLayerIndex(destinationLayerIndex);
        this.uiManager.destroyPluginElements(this.layers, this.background);
        this.uiManager.createPluginElements(this.layers);
        this.uiManager.destroyPixelCanvases(this.layers);   // TODO: Optimization: Instead of destroying all of the canvases only destroy and reorder the ones of interest
        this.uiManager.placeLayerCanvasesInDiva(this.layers);
        this.uiManager.placeLayerCanvasesInDiva(this.background);
        this.uiManager.highlightLayerSelectorById(this.layers[this.selectedLayerIndex].layerId);
        this.redrawAllLayers();
    }

    /**
     * -----------------------------------------------
     *                Keyboard Events
     * -----------------------------------------------
     **/

    // Actions on key release
    onKeyUp (e)
    {
        const KEY_1 = 49;
        const KEY_9 = 57;

        let lastLayer = this.selectedLayerIndex,
            key = e.keyCode ? e.keyCode : e.which;


        // Selecting a Layer using keyboard shortcutkeys 1 to 9
        if (key >= KEY_1 && key <= KEY_9)
        {
            try
            {
                this.uiManager.highlightLayerSelectorById(key - KEY_1 + 1);
            }
            catch (e)
            {
                if (e instanceof CannotSelectLayerException)
                {
                    alert(e.message);
                }
            }

            if (lastLayer !== this.selectedLayerIndex && this.mousePressed)
                this.layerChangedMidDraw = true;
        }

        switch (e.key.toLowerCase())
        {
            case "shift":
                this.shiftDown = false;
                break;
            case "h":
                this.layers[this.selectedLayerIndex].toggleLayerActivation();
        }
    }

    onKeyDown (e)
    {
        switch (e.key.toLowerCase())
        {
            case "[":
                console.log(this.selectedLayerIndex);
                if (this.selectedLayerIndex !== 0)
                    this.reorderLayers(this.selectedLayerIndex, this.selectedLayerIndex - 1);
                else
                {
                    //TODO: throw layer is already lowest layer exception
                }
                break;
            case "]":
                if (this.selectedLayerIndex !== this.layers.length - 1)
                    this.reorderLayers(this.selectedLayerIndex, this.selectedLayerIndex + 1);
                else
                {
                    //TODO: throw layer is already highest layer exception
                }
                break;
            case "escape":
                if (this.selection !== null)
                {
                    if (this.selection.imageData === null)
                    {
                        this.selection.clearSelection(this.core.getSettings().maxZoomLevel);
                    }
                }
                break;
            case "backspace":
                //FIXME: is it also "backspace" for windows?
                try
                {
                    if (e.ctrlKey || e.metaKey)                 // Cmd + Delete
                    {
                        this.deleteLayer();
                    }
                }
                catch (e)
                {
                    if (e instanceof CannotDeleteLayerException)
                    {
                        alert(e.message);
                    }
                }
                break;
            case "n":
                if (e.ctrlKey || e.metaKey)
                {
                    this.createLayer();                         // Cmd + N
                }
                break;
            case "z":
                if ((e.ctrlKey || e.metaKey) && e.shiftKey)     // Cmd + Shift + Z
                    this.redoAction();
                else if (e.ctrlKey || e.metaKey)                // Cmd + Z
                    this.undoAction();
                break;
            case "c":
                if (e.ctrlKey || e.metaKey)                     // Cmd + c
                    this.selection.copyShape(this.core.getSettings().maxZoomLevel);
                break;
            case "x":
                if (e.ctrlKey || e.metaKey)                     // Cmd + x
                    this.selection.cutShape(this.core.getSettings().maxZoomLevel);
                break;
            case "v":
                if (e.ctrlKey || e.metaKey)                     // Cmd + v
                {
                    if (this.selection !== null)
                    {
                        if (this.selection.imageData !== null)
                        {
                            this.selection.pasteShapeToLayer(this.layers[this.selectedLayerIndex]);
                            this.selection = null;
                            this.redrawLayer(this.layers[this.selectedLayerIndex]);
                        }
                    }
                }
                break;
            case "shift":
                this.shiftDown = true;
                break;
            case "f":
                this.core.publicInstance.toggleFullscreenMode();
                break;
            case "b":
                this.tools.setCurrentTool(this.tools.type.brush);
                break;
            case "r":
                this.tools.setCurrentTool(this.tools.type.rectangle);
                break;
            case "g":
                this.tools.setCurrentTool(this.tools.type.grab);
                break;
            case "e":
                this.tools.setCurrentTool(this.tools.type.erase);
                break;
            case "s":
                this.tools.setCurrentTool(this.tools.type.select);
                break;
            //FIXME: Current implementation continuously toggles layer activation on key hold. Should happen once on first key press
            case "m":
                this.layers[this.selectedLayerIndex].toggleLayerActivation();
                break;
            case "h":
                if (this.layers[this.selectedLayerIndex].isActivated())
                    this.layers[this.selectedLayerIndex].toggleLayerActivation();
                break;
        }
    }

    editLayerName (e, layerName, layerDiv, outsideClick, duringSwap, layer)
    {
        const RETURN_KEY = 13;

        // TODO: Find a way to unsubscribe from keyboard events while allowing enter key to be pressed
        layerDiv.removeAttribute("draggable");
        layerDiv.setAttribute("draggable", "false");

        let key = e.which || e.keyCode;
        if (key === RETURN_KEY || outsideClick)
        {
            if (duringSwap === false)
            {
                // TODO: Resubscribe to mouse events
                layer.updateLayerName(layerName.value);
                layerName.setAttribute("readonly", "true");
                layerDiv.setAttribute("draggable", "true");
            }
            else if (duringSwap === true)
            {
                //do nothing
            }
        }
    }

    /**
     * -----------------------------------------------
     *                Mouse Events
     * -----------------------------------------------
     **/

    getMousePos (canvas, evt)
    {
        let rect = canvas.getBoundingClientRect();

        return {
            x: evt.clientX - rect.left,
            y: evt.clientY - rect.top
        };
    }

    /*
        +===========+=======================+=======================+
        |   tool    |       Left Click      |       Right Click     |
        +===========+=======================+=======================+
        |   Brush   |     Freeform paint    |         Resize        |
        +–––––––––––+–––––––––––––––––––––––+–––––––––––––––––––––––+
        | Rectangle |     Rectangle draw    |    Rectangle Erase    |
        +–––––––––––+–––––––––––––––––––––––+–––––––––––––––––––––––+
        |   Grab    |       Drag scroll     |       Drag scroll     |
        +–––––––––––+–––––––––––––––––––––––+–––––––––––––––––––––––+
        |   Erase   |     Freeform erase    |         Resize        |
        +–––––––––––+–––––––––––––––––––––––+–––––––––––––––––––––––+
        |   Select  |    Rectangle Select   |    Rectangle Select   |
        +===========+=======================+=======================+
                Tools' behaviour on left and right mouse clicks
     */

    // Initializes tool actions
    onMouseDown (evt)
    {
        let mouseClickDiv = document.getElementById("diva-1-outer"),
            mousePos = this.getMousePos(mouseClickDiv, evt);

        // Clear Selection
        if (this.selection !== null)
            this.selection.clearSelection(this.core.getSettings().maxZoomLevel);

        if (evt.which === 1)
            this.rightMousePressed = false;
        if (evt.which === 3)
            this.rightMousePressed = true;

        this.mousePressed = true;
        switch (this.tools.getCurrentTool())
        {
            case this.tools.type.brush:
                if (this.rightMousePressed)
                    this.initializeBrushSizeChange(mousePos);
                else
                    this.initializeNewPathInCurrentLayer(mousePos);
                break;
            case this.tools.type.rectangle:
                this.initializeRectanglePreview(mousePos);
                break;
            case this.tools.type.grab:
                mouseClickDiv.style.cursor = "-webkit-grabbing";    // Change grab cursor to grabbing
                break;
            case this.tools.type.erase:
                if (this.rightMousePressed)
                    this.initializeBrushSizeChange(mousePos);
                else
                    this.initializeNewPathInCurrentLayer(mousePos);
                break;
            case this.tools.type.select:
                this.selection = new Selection();
                this.initializeRectanglePreview(mousePos);
                break;
            default:
        }
        // FIXME: At deactivation mouse is down so it clears the actions to redo
        this.undoneActions = [];
    }

    onMouseMove (evt)
    {
        let mouseClickDiv = document.getElementById("diva-1-outer"),
            mousePos = this.getMousePos(mouseClickDiv, evt);

        switch (this.tools.getCurrentTool())
        {
            case this.tools.type.brush:
                if (this.rightMousePressed)
                    this.changeBrushSize(mousePos);
                else
                    this.addPointToCurrentPath(mousePos);
                this.uiManager.moveBrushCursor(mousePos);
                break;
            case this.tools.type.rectangle:
                this.rectanglePreview(mousePos);
                break;
            case this.tools.type.erase:
                if (this.rightMousePressed)
                    this.changeBrushSize(mousePos);
                else
                    this.addPointToCurrentPath(mousePos);
                this.uiManager.moveBrushCursor(mousePos);
                break;
            case this.tools.type.select:
                this.rectanglePreview(mousePos);
                break;
            default:
        }
    }

    onMouseUp ()
    {
        let mouseClickDiv = document.getElementById("diva-1-outer");
        this.mousePressed = false;
        this.rightMousePressed = false;
        this.horizontalMove = false;
        this.initialShiftPress = true;

        switch (this.tools.getCurrentTool())
        {
            case this.tools.type.rectangle:
                // TODO: Add action: resized rectangle.
                // This is useful if a user wants to undo a rectangle resize (when implemented)
                break;
            case this.tools.type.grab:
                mouseClickDiv.style.cursor = "-webkit-grab";
                break;
            default:
        }
    }

    /**
     * -----------------------------------------------
     *            Delete / Create New Layer
     * -----------------------------------------------
     **/

    deleteLayer ()
    {
        let currentLayersLength = this.layers.length;

        // Enable function only if in standalone Pixel 
        if (typeof numberInputLayers === 'undefined') {
            // Continue
        } else {
            return;
        }

        if (currentLayersLength <= 1)
            throw new CannotDeleteLayerException("Must at least have one layer other than the background");

        this.uiManager.destroyPluginElements(this.layers, this.background);
        this.layers.splice(this.selectedLayerIndex, 1);

        //reset to the first layer on delete
        this.selectedLayerIndex = 0;

        //refreshing the layers view to reflect changes
        this.uiManager.createPluginElements(this.layers);
        this.redrawAllLayers();
    }

    createLayer ()
    { 
        // Enable function only if in standalone Pixel
        if (typeof numberInputLayers === 'undefined') {
            // Continue
        } else {
            return;
        }

        let colour;

        switch (this.layerIdCounter)
        {
            case 1:
                colour = new Colour(51, 102, 255, 1);
                break;
            case 2:
                colour = new Colour(255, 51, 102, 1);
                break;
            case 3:
                colour = new Colour(255, 255, 10, 1);
                break;
            case 4:
                colour = new Colour(2, 136, 0, 1);
                break;
            case 5:
                colour = new Colour(96, 0, 186, 1);
                break;
            case 6:
                colour = new Colour(239, 143, 0, 1);
                break;
            case 7:
                colour = new Colour(71, 239, 200, 1);
                break;
            case 8:
                colour = new Colour(247, 96, 229, 1);
                break;
            case 9:
                colour = new Colour(114, 61, 0, 1);
                break;
            default:
                colour = new Colour(parseInt(255 * Math.random()), parseInt(255 * Math.random()), parseInt(255 * Math.random()), 1);
        }

        let layer = new Layer(this.layerIdCounter, colour, "Layer " + this.layerIdCounter, this, 0.5);

        this.layerIdCounter++;
        this.layers.push(layer);

        this.changeCurrentlySelectedLayerIndex(this.layers.length - 1);
        this.uiManager.destroyPluginElements(this.layers, this.background);
        this.uiManager.createPluginElements(this.layers);

        this.redrawAllLayers();
    }

    /**
     * -----------------------------------------------
     *                   Undo / Redo
     * -----------------------------------------------
     **/

    redoAction ()
    {
        if (this.undoneActions.length > 0)
        {
            let actionToRedo = this.undoneActions[this.undoneActions.length - 1];

            if (!actionToRedo.layer.isActivated())
                return;

            switch (actionToRedo.object.type)
            {
                case "path":
                    actionToRedo.layer.addPathToLayer(actionToRedo.object);
                    break;
                case "shape":
                    actionToRedo.layer.addShapeToLayer(actionToRedo.object);
                    break;
                case "selection":
                    actionToRedo.layer.addToPastedRegions(actionToRedo.object);
                    break;
                default:
            }

            this.undoneActions.splice(this.undoneActions.length - 1, 1);    // Remove last element from undoneActions
            this.redrawLayer(actionToRedo.layer);
        }
    }

    undoAction ()
    {
        if (this.actions.length > 0)
        {
            let actionToRemove = this.actions[this.actions.length - 1];

            if (!actionToRemove.layer.isActivated())
                return;

            this.undoneActions.push(actionToRemove);
            this.removeActionAtIndex(this.actions.length - 1);
        }
    }

    removeActionAtIndex (index)
    {
        if (this.actions.length > 0 && this.actions.length >= index)
        {
            let actionToRemove = this.actions[index];
            this.removeAction(actionToRemove);
        }
    }

    removeAction (action)
    {
        if (action === null)
            return;

        switch (action.object.type)
        {
            case "path":
                action.layer.removePathFromLayer(action.object);
                break;
            case "shape":
                action.layer.removeShapeFromLayer(action.object);
                break;
            case "selection":
                action.layer.removeSelectionFromLayer(action.object);
                break;
            default:
        }

        // Get index of the action and remove it from the array
        this.redrawLayer(action.layer);
    }

    /**
     * ===============================================
     *                   Drawing
     * ===============================================
     **/

    /*
        1. Checks if drawing is valid
        2. Initializes a Path object in the selected layer and chooses its blend mode depending on the current tool
        3. Adds a point to the newly initialized path
        4. Specifies the zoomLevel at which the point will be drawn
     */
    initializeNewPathInCurrentLayer (mousePos)
    {
        // Layer is inactive
        if (!this.layers[this.selectedLayerIndex].isActivated())
            return;

        // Drawing on another page
        if (this.core.getSettings().currentPageIndex !== this.layers[0].pageIndex)
            return;

        // Get settings under the current zoomLevel
        let pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().zoomLevel,
            renderer = this.core.getSettings().renderer,
            relativeCoords = new Point().getRelativeCoordinatesFromPadded(pageIndex, renderer, mousePos.x, mousePos.y, zoomLevel);

        // Make sure user is not drawing outside of a diva page
        if (this.uiManager.isInPageBounds(relativeCoords.x, relativeCoords.y))
        {
            let selectedLayer = this.layers[this.selectedLayerIndex],
                point = new Point(relativeCoords.x, relativeCoords.y, pageIndex),
                brushSize = this.uiManager.getBrushSizeSelectorValue();

            this.lastRelCoordX = relativeCoords.x;
            this.lastRelCoordY = relativeCoords.y;

            // Create New Path in Layer
            if (this.tools.getCurrentTool() === this.tools.type.brush)
            {
                selectedLayer.createNewPath(brushSize, "add");
                selectedLayer.addToCurrentPath(point, "add");
            }
            else if (this.tools.getCurrentTool() === this.tools.type.erase)
            {
                selectedLayer.createNewPath(brushSize, "subtract");
                selectedLayer.addToCurrentPath(point, "subtract");
            }

            // Draw in max zoom level
            zoomLevel = this.core.getSettings().maxZoomLevel;
            selectedLayer.getCurrentPath().connectPoint(selectedLayer, point, pageIndex, zoomLevel, false, this.core.getSettings().renderer, selectedLayer.getCanvas(), "page");
        }
        else
        {
            this.mousePressed = false;
        }
    }

    /*
         1. Checks if drawing is valid
         2. Specifies the coordinates of the point to be drawn depending on shift press
         3. Adds a point to the current path being edited in the current layer
         4. Connects the new point to the previous point in the current path and draws it
     */
    addPointToCurrentPath (mousePos)
    {
        if (!this.layers[this.selectedLayerIndex].isActivated())
            return;

        // Drawing on another page
        if (this.core.getSettings().currentPageIndex !== this.layers[0].pageIndex)
            return;

        if (!this.mousePressed)
            return;

        let point,
            pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().zoomLevel,
            renderer = this.core.getSettings().renderer,
            relativeCoords = new Point().getRelativeCoordinatesFromPadded(pageIndex, renderer, mousePos.x, mousePos.y, zoomLevel);

        if (!this.uiManager.isInPageBounds(relativeCoords.x, relativeCoords.y))
            return;

        if (!this.layerChangedMidDraw)
        {
            let pageIndex = this.core.getSettings().currentPageIndex,
                zoomLevel = this.core.getSettings().maxZoomLevel;

            // Draw straight lines
            if (this.mousePressed && this.shiftDown)
            {
                // If this is the first time shift is pressed, calculate the direction of the line
                if (this.initialShiftPress)
                {
                    // this.lastRelCoordX/Y hold saved path coordinates that help drawing a straight line
                    // They are not updated when the straight line is being drawn
                    if (Math.abs(relativeCoords.x - this.lastRelCoordX) >= Math.abs(relativeCoords.y - this.lastRelCoordY))
                        this.horizontalMove = true;

                    this.initialShiftPress = false;
                }

                if (!this.horizontalMove)
                    point = new Point(this.lastRelCoordX, relativeCoords.y, pageIndex);
                else
                    point = new Point(relativeCoords.x, this.lastRelCoordY, pageIndex);
            }
            else
            {
                this.horizontalMove = false;
                this.initialShiftPress = true;
                this.lastRelCoordX = relativeCoords.x;
                this.lastRelCoordY = relativeCoords.y;
                point = new Point(relativeCoords.x, relativeCoords.y, pageIndex);
            }

            // Add new point to the current path
            switch (this.tools.getCurrentTool())
            {
                case this.tools.type.brush:
                    this.layers[this.selectedLayerIndex].addToCurrentPath(point, "add");
                    break;
                case this.tools.type.erase:
                    this.layers[this.selectedLayerIndex].addToCurrentPath(point, "subtract");
                    break;
                default:
                    this.layers[this.selectedLayerIndex].addToCurrentPath(point, "add");
            }

            let layer = this.layers[this.selectedLayerIndex];
            layer.getCurrentPath().connectPoint(layer, point, pageIndex, zoomLevel, true, this.core.getSettings().renderer, layer.getCanvas(), "page");

            return;
        }

        // If layer changed mid drawing then create a new path on selected layer
        this.initializeNewPathInCurrentLayer(mousePos);
        this.layerChangedMidDraw = false;
    }

    /*
        1. Checks if drawing is valid
        2. Creates a Rectangle object in the selected layer and chooses its mode depending on the current tool
     */
    initializeRectanglePreview (mousePos)
    {
        if (!this.layers[this.selectedLayerIndex].isActivated())
            return;

        // Drawing on another page
        if (this.core.getSettings().currentPageIndex !== this.layers[0].pageIndex)
            return;

        let pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().zoomLevel,
            renderer = this.core.getSettings().renderer,
            relativeCoords = new Point().getRelativeCoordinatesFromPadded(pageIndex, renderer, mousePos.x, mousePos.y, zoomLevel);

        if (this.uiManager.isInPageBounds(relativeCoords.x, relativeCoords.y))
        {
            let selectedLayer = this.layers[this.selectedLayerIndex];

            switch (this.tools.getCurrentTool())
            {
                case this.tools.type.select:
                    selectedLayer.addShapeToLayer(new Rectangle(new Point(relativeCoords.x,relativeCoords.y,pageIndex), 0, 0, "select", this.tools.getCurrentTool()));
                    this.selection.setSelectedShape(selectedLayer.getCurrentShape(), this.layers[this.selectedLayerIndex]);
                    break;
                case this.tools.type.rectangle:
                    if (this.rightMousePressed)
                        selectedLayer.addShapeToLayer(new Rectangle(new Point(relativeCoords.x,relativeCoords.y,pageIndex), 0, 0, "subtract", this.tools.getCurrentTool()));
                    else
                        selectedLayer.addShapeToLayer(new Rectangle(new Point(relativeCoords.x,relativeCoords.y,pageIndex), 0, 0, "add", this.tools.getCurrentTool()));
                    break;
                default:
            }

            this.redrawLayer(selectedLayer);
        }
    }

    /*
        1. Checks if drawing is valid
        2. Updates the height and width of the current rectangle in the selected layer depending on mouse position
           or shift press (square)
        3. Creates a new Rectangle if the layer was changed mid draw
     */
    rectanglePreview (mousePos)
    {
        if (!this.layers[this.selectedLayerIndex].isActivated())
            return;

        // Drawing on another page
        if (this.core.getSettings().currentPageIndex !== this.layers[0].pageIndex)
            return;

        if (!this.layerChangedMidDraw)
        {
            if (!this.mousePressed)
                return;

            let pageIndex = this.core.getSettings().currentPageIndex,
                zoomLevel = this.core.getSettings().zoomLevel,
                renderer = this.core.getSettings().renderer,
                relativeCoords = new Point().getRelativeCoordinatesFromPadded(pageIndex, renderer, mousePos.x, mousePos.y, zoomLevel),
                rectangle = this.layers[this.selectedLayerIndex].getCurrentShape();

            if (!this.uiManager.isInPageBounds(relativeCoords.x, relativeCoords.y))
                return;

            let lastWidth = rectangle.relativeRectWidth;
            rectangle.relativeRectWidth = relativeCoords.x - rectangle.origin.relativeOriginX;

            // Draw square
            if (this.shiftDown)
            {
                let mainDiagonal;

                if (this.isInMainDiagonal(relativeCoords, rectangle))
                    mainDiagonal = 1;
                else
                    mainDiagonal = -1;

                let squareInBounds = this.uiManager.isInPageBounds(rectangle.origin.relativeOriginX + rectangle.relativeRectWidth,
                    rectangle.origin.relativeOriginY + (mainDiagonal * rectangle.relativeRectWidth));

                if (squareInBounds)
                    rectangle.relativeRectHeight = mainDiagonal * rectangle.relativeRectWidth;
                else
                    rectangle.relativeRectWidth = lastWidth;
            }
            else
            {
                rectangle.relativeRectHeight = relativeCoords.y - rectangle.origin.relativeOriginY;
            }

            this.redrawLayer(this.layers[this.selectedLayerIndex]);
        }
        else
        {
            // Create a new rectangle to which the change will be
            this.layerChangedMidDraw = false;
            this.initializeRectanglePreview(mousePos);
        }
    }

    initializeBrushSizeChange (mousePos)
    {
        let brushSizeSlider = document.getElementById("brush-size-selector");
        this.prevMouseX = mousePos.x;
        this.prevSize = brushSizeSlider.value;
    }

    changeBrushSize (mousePos)
    {
        let brushSizeSlider = document.getElementById("brush-size-selector"),
            mouseXVariation = 0.1 * (parseFloat(mousePos.x) - parseFloat(this.prevMouseX));
        //Start at the current brush size when varying
        brushSizeSlider.value = parseFloat(this.prevSize) + mouseXVariation;

        this.uiManager.resizeBrushCursor();
    }

    // TODO: Generalize so that function returns any general relative position using enums
    /**
     * Returns true if the relative coordinates provided are on the main diagonal of the origin of the shape (south east or
     * north west of the origin) otherwise returns false
     * @param relativeCoords
     * @param shape
     * @returns {boolean}
     */
    isInMainDiagonal (relativeCoords, shape)
    {
        if (relativeCoords.x < shape.origin.relativeOriginX && relativeCoords.y < shape.origin.relativeOriginY)
            return true;
        else if (relativeCoords.x > shape.origin.relativeOriginX && relativeCoords.y > shape.origin.relativeOriginY)
            return true;

        return false;
    }

    redrawLayer (layer)
    {
        layer.drawLayer(this.core.getSettings().maxZoomLevel, layer.getCanvas());
    }

    redrawAllLayers ()
    {
        this.layers.forEach ((layer) =>
        {
            this.redrawLayer(layer);
        });
    }

    changeCurrentlySelectedLayerIndex (newIndex)
    {
        this.selectedLayerIndex = newIndex;
        if (this.selection !== null)
        {
            if (this.selection.imageData === null)
            {
                this.selection.clearSelection(this.core.getSettings().maxZoomLevel);
            }
        }
    }

    /**
     * ===============================================
     *                    Export
     * ===============================================
     **/

    // Will fill a canvas with the highlighted data and scan every pixel of that and fill another canvas with diva data
    // on the highlighted regions
    exportAsImageData ()
    {
        //FIXME: Force Diva to highest zoom level to be able to get the pixel data
        let pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().zoomLevel;

        new Export(this, this.layers, pageIndex, zoomLevel, this.uiManager).exportLayersAsImageData();
    }

    exportAsPNG ()
    {
        let pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().zoomLevel;

        new Export(this, this.layers, pageIndex, zoomLevel, this.uiManager).exportLayersAsPNG();
    }

    exportAsCSV ()
    {
        let pageIndex = this.core.getSettings().currentPageIndex,
            zoomLevel = this.core.getSettings().maxZoomLevel;

        new Export(this, this.layers, pageIndex, zoomLevel, this.uiManager).exportLayersAsCSV();
    }

    /**
     * ===============================================
     *                    Import
     * ===============================================
     **/
    importPNGToLayer (e)
    {
        new Import(this, this.layers, this.core.getSettings().currentPageIndex, this.core.getSettings().zoomLevel, this.uiManager).uploadLocalImageToLayer(this.layers[this.selectedLayerIndex], e);
    }
}

PixelPlugin.prototype.pluginName = "pixel";
PixelPlugin.prototype.isPageTool = true;

/**
 * Make this plugin available in the global context
 * as part of the 'Diva' namespace.
 **/
(function (global)
{
    global.Diva.PixelPlugin = PixelPlugin;
})(window);