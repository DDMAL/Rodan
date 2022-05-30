/*jshint esversion: 6 */
import {Path} from './path';
import {Point} from './point';
import {Action} from './action';

export class Layer
{
    constructor (layerId, colour, layerName, pixelInstance, layerOpacity)
    {
        this.layerId = layerId;
        this.shapes = [];
        this.paths = [];
        this.colour = colour;
        this.layerName = layerName;
        this.canvas = null;
        this.ctx = null;
        this.actions = [];
        this.activated = true;
        this.layerOpacity = layerOpacity;
        this.pixelInstance = pixelInstance;
        this.pageIndex = this.pixelInstance.core.getSettings().currentPageIndex;
        this.backgroundImageCanvas = null;
        this.pastedRegions = [];
        this.cloneCanvas();
    }

    /**
     * Creates a layer canvas that is the same size as a page in diva
     */
    cloneCanvas ()
    {
        let maxZoomLevel = this.pixelInstance.core.getSettings().maxZoomLevel;

        let height = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, maxZoomLevel).height,
            width = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, maxZoomLevel).width;

        this.canvas = document.createElement('canvas');
        this.canvas.setAttribute("class", "pixel-canvas");
        this.canvas.setAttribute("id", "layer-" + this.layerId + "-canvas");
        this.canvas.width = width;
        this.canvas.height = height;

        this.ctx = this.canvas.getContext('2d');

        this.resizeLayerCanvasToZoomLevel(this.pixelInstance.core.getSettings().zoomLevel);
        this.placeLayerCanvasOnTopOfEditingPage();

        this.backgroundImageCanvas = document.createElement("canvas");
        this.backgroundImageCanvas.width = this.canvas.width;
        this.backgroundImageCanvas.height = this.canvas.height;
    }

    resizeLayerCanvasToZoomLevel (zoomLevel)
    {
        let floorZoom = Math.floor(zoomLevel),
            extra = zoomLevel - floorZoom,
            scaleRatio = Math.pow(2, extra);

        let height = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, floorZoom).height,
            width = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, floorZoom).width;

        width *= scaleRatio;
        height *= scaleRatio;

        this.canvas.style.width = width + "px";
        this.canvas.style.height = height + "px";

        this.placeLayerCanvasOnTopOfEditingPage();

        if (this.pixelInstance.uiManager !== null)
            this.pixelInstance.uiManager.resizeBrushCursor();
    }

    placeLayerCanvasOnTopOfEditingPage ()
    {
        let zoomLevel = this.pixelInstance.core.getSettings().zoomLevel;

        let coords = new Point (0,0,0).getCoordsInViewport(zoomLevel, this.pageIndex, this.pixelInstance.core.getSettings().renderer);

        this.canvas.style.left = coords.x + "px";
        this.canvas.style.top = coords.y + "px";
    }

    placeCanvasAfterElement (element)
    {
        element.parentNode.insertBefore(this.canvas, element.nextSibling);
    }

    getCanvas ()
    {
        return this.canvas;
    }

    getCtx ()
    {
        return this.ctx;
    }

    clearCtx ()
    {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    updateLayerName (newLayerName)
    {
        this.layerName = newLayerName;
    }

    addShapeToLayer (shape)
    {
        this.shapes.push(shape);
        this.addAction(new Action (shape, this));
    }

    addPathToLayer (path)
    {
        this.paths.push(path);
        this.addAction(new Action (path, this));
    }

    /**
     * Creates a new path that has the brush size selector width
     * @param point
     * @param blendMode
     */
    addToCurrentPath (point, blendMode)
    {
        if (this.paths.length === 0)
            this.createNewPath(this.pixelInstance.uiManager.getBrushSizeSelectorValue(), blendMode);

        this.paths[this.paths.length - 1].addPointToPath(point);
    }

    getCurrentPath ()
    {
        if (this.paths.length > 0)
            return this.paths[this.paths.length - 1];
        else
            return null;
    }

    createNewPath (brushSize, blendMode)
    {
        let path = new Path(brushSize, blendMode);
        this.paths.push(path);
        this.addAction(new Action (path, this));
    }

    removePathFromLayer (path)
    {
        let index = this.paths.indexOf(path);
        this.paths.splice(index, 1);

        this.actions.forEach((action) =>
        {
            if (action.object === path)
            {
                this.removeAction(action);
            }
        });
    }

    removeShapeFromLayer (shape)
    {
        let index = this.shapes.indexOf(shape);
        this.shapes.splice(index, 1);

        this.actions.forEach((action) =>
        {
            if (action.object === shape)
                this.removeAction(action);
        });
    }

    removeSelectionFromLayer (selection)
    {
        let index = this.pastedRegions.indexOf(selection);
        this.pastedRegions.splice(index, 1);

        this.actions.forEach((action) =>
        {
            if (action.object === selection)
                this.removeAction(action);
        });
    }

    setOpacity (opacity)
    {
        this.colour.alpha = opacity;
    }

    getOpacity ()
    {
        return this.colour.alpha;
    }

    getCurrentShape ()
    {
        if (this.shapes.length > 0)
        {
            return this.shapes[this.shapes.length - 1];
        }
        else
        {
            return null;
        }
    }

    isActivated ()
    {
        return this.activated;
    }

    setLayerOpacity (layerOpacity)
    {
        this.layerOpacity = layerOpacity;
    }

    getLayerOpacity ()
    {
        return this.layerOpacity;
    }

    getLayerOpacityCSSString ()
    {
        return "opacity : " + this.layerOpacity;
    }

    drawLayer (zoomLevel, canvas)
    {
        if (!this.isActivated())
            return;

        this.drawLayerInPageCoords(zoomLevel, canvas, this.pageIndex);
    }

    drawLayerInPageCoords (zoomLevel, canvas, pageIndex)
    {
        let ctx = canvas.getContext('2d');
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Redraw PreBinarized Image on layer canvas
        if (this.backgroundImageCanvas !== null)
            ctx.drawImage(this.backgroundImageCanvas, 0, 0);

        // Redraw all actions
        this.actions.forEach ((action) =>
        {
            action.object.drawOnPage(this, pageIndex, zoomLevel, this.pixelInstance.core.getSettings().renderer, canvas);
        });
    }

    setBackgroundImageCanvas (canvas)
    {
        this.backgroundImageCanvas = canvas;
    }

    addToPastedRegions (selection)
    {
        this.pastedRegions.push(selection);
        this.addAction(new Action (selection, this));
    }

    addAction (action)
    {
        this.actions.push(action);

        // Selection is temporary and only concerns this layer thus no need to add to global actions
        if (!(action.object.type === "selection" && action.object.selectedShape.blendMode === "select"))
            this.pixelInstance.actions.push(action);
    }

    removeAction (action)
    {
        let actionIndex = this.actions.indexOf(action);
        this.actions.splice(actionIndex, 1);

        let globalActionIndex = this.pixelInstance.actions.indexOf(action);
        this.pixelInstance.actions.splice(globalActionIndex, 1);
    }

    displayColourOptions ()
    {
        // TODO: Implement function
        console.log("colour clicked here");
    }

    /**
     * Displays the layer options (such as opacity) as a drop down from the layer selectors
     */
    displayLayerOptions ()
    {
        let layerOptionsDiv = document.getElementById("layer-" + this.layerId + "-options");

        if (layerOptionsDiv.classList.contains("unchecked-layer-settings")) //It is unchecked, check it
        {
            layerOptionsDiv.classList.remove("unchecked-layer-settings");
            layerOptionsDiv.classList.add("checked-layer-settings");
            this.pixelInstance.uiManager.createOpacitySlider(this, layerOptionsDiv.parentElement.parentElement, layerOptionsDiv.parentElement);
        }
        else
        {
            layerOptionsDiv.classList.remove("checked-layer-settings");
            layerOptionsDiv.classList.add("unchecked-layer-settings");
            this.pixelInstance.uiManager.destroyOpacitySlider(this);
        }
    }

    /**
     * Visually displays a layer
     */
    activateLayer ()
    {
        let layerActivationDiv = document.getElementById("layer-" + this.layerId + "-activation");
        layerActivationDiv.classList.remove("layer-deactivated");
        layerActivationDiv.classList.add("layer-activated");
        this.getCanvas().style.opacity = this.getLayerOpacity();

        if (this.layerId === this.pixelInstance.background.layerId)      // Background
        {
            this.activated = true;
        }
        else
        {
            this.activated = true;
            this.pixelInstance.redrawLayer(this);
        }
    }

    deactivateLayer ()
    {
        let layerActivationDiv = document.getElementById("layer-" + this.layerId + "-activation");
        layerActivationDiv.classList.remove("layer-activated");
        layerActivationDiv.classList.add("layer-deactivated");
        this.activated = false;

        if (this.layerId === this.pixelInstance.background.layerId)      // Background
        {
            this.getCanvas().style.opacity = 0;
        }
        else
        {
            this.clearCtx();
        }
    }

    toggleLayerActivation ()
    {
        let layerActivationDiv = document.getElementById("layer-" + this.layerId + "-activation");
        if (layerActivationDiv.classList.contains("layer-deactivated"))
        {
            this.activateLayer();
        }
        else
        {
            this.deactivateLayer();
        }
    }
}