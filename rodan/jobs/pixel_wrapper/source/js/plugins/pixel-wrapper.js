import {Rectangle} from './pixel.js/source/rectangle';
import {Point} from './pixel.js/source/point';
import {Layer} from './pixel.js/source/layer';
import {Colour} from './pixel.js/source/colour';

export class PixelWrapper
{
    constructor (pixelInstance)
    {
        this.pixelInstance = pixelInstance;
        this.layers = pixelInstance.layers;
        this.totalRegionCount;
        this.uiManager = pixelInstance.uiManager;
        this.pageIndex = pixelInstance.core.getSettings().currentPageIndex;
        this.zoomLevel = pixelInstance.core.getSettings().zoomLevel;
        this.exportInterrupted = false;
        this.selectRegionLayer;
        this.selectedWholePage = false;
        this.maxZoom = pixelInstance.core.getSettings().maxZoomLevel;
        this.maxWidth = pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, this.maxZoom).width;
        this.maxHeight = pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(this.pageIndex, this.maxZoom).height;
    }

    activate ()
    {
        this.createLayers();
        this.createButtons();
        this.rodanImagesToCanvas();
        this.createTooltip();
        this.addListeners();
    }

    deactivate ()
    {
        this.destroyButtons();
    }

    addListeners ()
    {
        // add select all listener for select region layer
        document.addEventListener('keydown', (e) =>
        {
            if (this.pixelInstance.selectedLayerIndex === 0)
            {
                if (e.key.toLowerCase() === 'a' && e.shiftKey)
                    this.selectedWholePage = true;
                else if (e.keyCode === 27)
                    this.selectedWholePage = false;
                else
                    return;

                let mode = this.selectedWholePage ? 'add' : 'subtract';
                let rect = new Rectangle(new Point(0, 0, this.pageIndex), this.maxWidth, this.maxHeight, mode);
                this.selectRegionLayer.addShapeToLayer(rect);
                this.pixelInstance.redrawLayer(this.selectRegionLayer);
            }
        });
    }

    createTooltip ()
    {
        // Create help box next to selectRegionLayer selector
        let selectRegionLayerBox = document.getElementById("layer--1-selector");

        let helpDiv = document.createElement("div"),
            helpText = document.createTextNode("?"),
            tooltipDiv = document.createElement("div"),
            // string instead of textNode so newlines can be used
            tooltipText = "<p>While in the Select Region Layer, use the " +
            "rectangle tool to select the regions of the page that you will classify.</p>" +
            "<p>Once you select these regions, select another layer and begin classifying! " +
            "Keep in mind that classification outside these regions will not be utilized.</p>" +
            "<p>You can select the entire page by pressing <b>SHIFT + A</b>.</p>" +
            "<p>You can deselect the entire page by pressing <b>ESC</b>. This will destroy all selection regions " +
            "that you have created.</p>";

        helpDiv.setAttribute("class", "tooltip");
        helpDiv.appendChild(helpText);
        tooltipDiv.setAttribute("class", "tooltiptext");
        tooltipDiv.innerHTML = tooltipText;

        helpDiv.appendChild(tooltipDiv);
        selectRegionLayerBox.appendChild(helpDiv);
    }


    createButtons ()
    {
        let rodanExportButton = document.createElement("button"),
            rodanExportText = document.createTextNode("Submit To Rodan");

        this.exportToRodan = () => { this.createBackgroundLayer(); }; // This will call exportLayersToRodan when done

        rodanExportButton.setAttribute("id", "rodan-export-button");
        rodanExportButton.appendChild(rodanExportText);
        rodanExportButton.addEventListener("click", this.exportToRodan);

        document.body.insertBefore(rodanExportButton, document.getElementById('imageLoader'));
    }

    destroyButtons ()
    {
        let rodanExportButton = document.getElementById("rodan-export-button");

        rodanExportButton.parentNode.removeChild(rodanExportButton);
    }

    /**
     *  Creates the number of required layers based on the number of input ports in the Rodan job.
     *  The variable numberInputLayers is actually defined in the outermost index.html
     */
    createLayers ()
    {
        // Set default tool to rectangle (for select region layer)
        this.pixelInstance.tools.currentTool = "rectangle";

        // Only create default layers once
        if (this.layers.length !== 1)
            return;

        let numLayers = numberInputLayers;

        // Ask user how many layers to create if there's no input
        if (numberInputLayers === 0)
        {
            while (numLayers <= 0 || numLayers > 7)
            {
                numLayers = parseInt(prompt("How many layers will you classify?\n" +
                "This must be two (2) less than the total number of output ports.", 3));
            }
        }

        this.selectRegionLayer = new Layer(-1, new Colour(240, 232, 227, 1), "Select Region", this.pixelInstance, 0.3);
        this.layers.unshift(this.selectRegionLayer);

        // There is 1 active layer already created by default in PixelPlugin with layerId = 1,
        // so start at 2, and ignore one input layer which gets assigned to layer 1. Max 7 input
        for (var i = 2; i < numLayers + 1; i++)
        {
            let colour;
            switch (i)
            {
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
            }
            let layer = new Layer(i, colour, "Layer " + i, this.pixelInstance, 0.5);
            this.layers.push(layer);
        }

        this.pixelInstance.layerIdCounter = this.layers.length;

        // Refresh UI
        this.uiManager.destroyPluginElements(this.layers, this.pixelInstance.background);
        this.uiManager.createPluginElements(this.layers);
    }

    exportLayersToRodan ()
    {
        console.log("Exporting!");

        this.layers.push(this.selectRegionLayer);

        let count = this.layers.length;
        let urlList = [];

        this.layers.forEach((layer) =>
        {
            console.log(layer.layerId + " " + layer.layerName);

            let dataURL = layer.getCanvas().toDataURL();
            urlList.push(dataURL);
            count -= 1;
                if (count === 0)
                {
                    console.log(urlList);
                    console.log("done");

                    $.ajax({
                        url: '',
                        type: 'POST',
                        data: JSON.stringify({'user_input': urlList}),
                        contentType: 'application/json',
                        success: () => {
                            setTimeout(function(){ alert("Submission successful! Click OK to exit Pixel.js."); }, 1000);
                            setTimeout(function(){ window.close(); }, 1200);
                        },
                        error: (jqXHR, textStatus, errorThrown) => {
                            console.log(jqXHR);
                            console.log(textStatus);
                            console.log(errorThrown);
                            alert("An error occurred: " + errorThrown);
                        }
                    });
                }
        });
    }

    /**
     *  Generates a background layer by iterating over all the pixel data for each layer within the
     *  selection regions, and subtracting it from the background layer if the data is
     *  non-transparent (alpha != 0). Uses the uiManager progress bar and exports to Rodan when done
     */
    createBackgroundLayer ()
    {
        // Don't export selectRegionLayer to Rodan
        this.layers.shift();
        this.layersCount = this.layers.length;

        // NOTE: this backgroundLayer and the original background (image) both have layerId 0, but
        // this backgroundLayer is only created upon submitting (so no conflicts)
        let backgroundLayer = new Layer(0, new Colour(242, 0, 242, 1), "Background Layer",
            this.pixelInstance, 0.5, this.pixelInstance.actions);

        // Add select regions to backgroundLayer
        this.selectRegionLayer.shapes.forEach((shape) =>
        {
            // Get shape dimensions
            let x = shape.origin.getCoordsInPage(this.maxZoom).x,
                y = shape.origin.getCoordsInPage(this.maxZoom).y,
                rectWidth = shape.relativeRectWidth * Math.pow(2, this.maxZoom),
                rectHeight = shape.relativeRectHeight * Math.pow(2, this.maxZoom),
                rect = new Rectangle(new Point(x, y, this.pageIndex), rectWidth, rectHeight, "add");

            if (shape.blendMode === "subtract") {
                rect.changeBlendModeTo("subtract");
            }

            backgroundLayer.addShapeToLayer(rect);
        });
        backgroundLayer.drawLayer(this.maxZoom, backgroundLayer.getCanvas());

        // Alert and return if user hasn't created a selection region
        if (this.selectRegionLayer.shapes.length === 0)
        {
            alert("You haven't created any select regions!");
            this.layers.unshift(this.selectRegionLayer);
            return;
        }

        // Instantiate progress bar
        // this.uiManager.createExportElements(this);
        // Draw select region layer on bg layer
        this.selectRegionLayer.drawLayerInPageCoords(this.maxZoom, backgroundLayer.getCanvas(), this.pageIndex);
        let ctx = backgroundLayer.getCtx();
        // Remove parts of user-defined layers from bg
        ctx.globalCompositeOperation = "destination-out";

        this.layers.forEach((layer) =>
        {
            // Create layer canvas and draw (so pixel data can be accessed)
            let layerCanvas = document.createElement('canvas');
            layerCanvas.setAttribute("class", "export-page-canvas");
            layerCanvas.setAttribute("id", "layer-" + layer.layerId + "-export-canvas");
            layerCanvas.setAttribute("style", "position: absolute; top: 0; left: 0;");
            layerCanvas.width = this.maxWidth;
            layerCanvas.height = this.maxHeight;
            layer.drawLayerInPageCoords(this.maxZoom, layerCanvas, this.pageIndex);

            if (layer.layerId !== 0) {
              ctx.drawImage(layerCanvas, 0, 0);
            }
        });
        this.layers.unshift(backgroundLayer);
        this.exportLayersToRodan();
    }

    /**
     *  Handles the Rodan input layers and draws them on each layer in Pixel
     */
    rodanImagesToCanvas ()
    {
        this.layers.forEach((layer) =>
        {
            let img = document.getElementById("layer" + layer.layerId +"-img");
            if (img !== null)
            {
                let imageCanvas = document.createElement("canvas");
                imageCanvas.width = layer.getCanvas().width;
                imageCanvas.height = layer.getCanvas().height;
                let ctx = imageCanvas.getContext("2d");

                ctx.drawImage(img, 0, 0);

                let imageData = ctx.getImageData(0, 0, layer.getCanvas().width, layer.getCanvas().height),
                    data = imageData.data;

                for(let i = 0; i < data.length; i += 4)
                {
                    data[i] = layer.colour.red;             // red
                    data[i + 1] = layer.colour.green;       // green
                    data[i + 2] = layer.colour.blue;        // blue
                }
                // overwrite original image
                ctx.putImageData(imageData, 0, 0);

                layer.backgroundImageCanvas = imageCanvas;
                layer.drawLayer(this.pixelInstance.core.getSettings().maxZoomLevel, layer.getCanvas());
            }
        });
    }
}
