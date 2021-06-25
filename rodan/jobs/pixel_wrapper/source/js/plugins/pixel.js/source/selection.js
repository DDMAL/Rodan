/*jshint esversion: 6 */
export class Selection
{
    constructor ()
    {
        this.layer = null;
        this.selectedShape = null;
        this.type = "selection";
        this.imageData = null;
    }

    copyShape (maxZoomLevel)
    {
        this.layer.removeShapeFromLayer(this.selectedShape);
        this.layer.drawLayer(maxZoomLevel, this.layer.getCanvas());

        let scaleRatio = Math.pow(2, maxZoomLevel);

        // Get coordinates of the selection shape (a rectangle here)
        let absoluteRectOriginX = this.selectedShape.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.selectedShape.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.selectedShape.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.selectedShape.relativeRectHeight * scaleRatio;

        let xmin = Math.min(absoluteRectOriginX, absoluteRectOriginX + absoluteRectWidth),
            ymin = Math.min(absoluteRectOriginY, absoluteRectOriginY + absoluteRectHeight);

        let selectedLayerCtx = this.layer.getCanvas().getContext("2d");
        let imageData = selectedLayerCtx.getImageData(xmin, ymin, Math.abs(absoluteRectWidth), Math.abs(absoluteRectHeight));

        this.imageData = imageData;

        this.selectedShape.changeBlendModeTo("add");
    }

    cutShape (maxZoomLevel)
    {
        this.layer.removeShapeFromLayer(this.selectedShape);
        this.layer.drawLayer(maxZoomLevel, this.layer.getCanvas());

        let scaleRatio = Math.pow(2, maxZoomLevel);

        // Get coordinates of the selection shape (a rectangle here)
        let absoluteRectOriginX = this.selectedShape.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.selectedShape.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.selectedShape.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.selectedShape.relativeRectHeight * scaleRatio;

        let xmin = Math.min(absoluteRectOriginX, absoluteRectOriginX + absoluteRectWidth),
            ymin = Math.min(absoluteRectOriginY, absoluteRectOriginY + absoluteRectHeight);

        let selectedLayerCtx = this.layer.getCanvas().getContext("2d");
        let imageData = selectedLayerCtx.getImageData(xmin, ymin, Math.abs(absoluteRectWidth), Math.abs(absoluteRectHeight));

        this.imageData = imageData;

        this.selectedShape.changeBlendModeTo("subtract");
        this.layer.addShapeToLayer(this.selectedShape);
        this.layer.drawLayer(maxZoomLevel, this.layer.getCanvas());
    }

    /**
     * Must redraw layer after calling
     * @param layerToPasteTo
     * @param maxZoomLevel
     */
    pasteShapeToLayer (layerToPasteTo)
    {
        let data = this.imageData.data;

        // Change imageData colour to layer's colour
        for (let i = 0; i < data.length; i += 4)
        {
            data[i] = layerToPasteTo.colour.red;             // red
            data[i + 1] = layerToPasteTo.colour.green;       // green
            data[i + 2] = layerToPasteTo.colour.blue;        // blue
        }
        layerToPasteTo.addToPastedRegions(this);
    }

    setSelectedShape (selectedShape, selectedLayer)
    {
        this.selectedShape = selectedShape;
        this.layer = selectedLayer;
    }

    clearSelection (maxZoomLevel)
    {
        if (this.layer !== null && this.selectedShape !== null)
        {
            if (this.selectedShape.blendMode === "select")
                this.layer.removeShapeFromLayer(this.selectedShape);
            this.layer.drawLayer(maxZoomLevel, this.layer.getCanvas());
        }
    }

    drawOnPage (layer, pageIndex, zoomLevel, renderer, canvas)
    {
        let scaleRatio = Math.pow(2, zoomLevel);

        // Get coordinates of the selection shape (a rectangle here)
        let absoluteRectOriginX = this.selectedShape.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.selectedShape.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.selectedShape.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.selectedShape.relativeRectHeight * scaleRatio;

        let xmin = Math.min(absoluteRectOriginX, absoluteRectOriginX + absoluteRectWidth);
        let ymin = Math.min(absoluteRectOriginY, absoluteRectOriginY + absoluteRectHeight);

        let pasteCanvas = document.createElement("canvas");
        pasteCanvas.width = Math.abs(absoluteRectWidth);
        pasteCanvas.height = Math.abs(absoluteRectHeight);

        pasteCanvas.getContext("2d").putImageData(this.imageData, 0, 0);

        canvas.getContext("2d").drawImage(pasteCanvas, xmin, ymin);
    }
}
