/*jshint esversion: 6 */
import {Point} from './point';
import
{
    CannotDeleteLayerException,
    CannotSelectLayerException
} from "./exceptions";

export class UIManager
{
    constructor (pixelInstance)
    {
        this.pixelInstance = pixelInstance;

        this.mouse = {
            x: 0,
            y: 0,
            startX: 0,
            startY: 0
        };
    }

    createPluginElements (layers)
    {
        this.placeLayerCanvasesInDiva(layers);
        this.createUndoButton();
        this.createRedoButton();
        // Enable buttons only if in standalone Pixel 
        if (typeof numberInputLayers === 'undefined') {
            this.createDeleteLayerButton();
            this.createCreateLayerButton();
        }
        this.createLayersView(layers);
        this.createToolsView(this.pixelInstance.tools.getAllTools());
        this.createExportButtons();
        this.createImportButtons();
    }

    destroyPluginElements (layers, background)
    {
        this.destroyLayerSelectors(layers);
        this.destroyBrushSizeSelector();
        this.destroyUndoButton();
        this.destroyRedoButton();
        // Enable buttons only if in standalone Pixel 
        if (typeof numberInputLayers === 'undefined') {
            this.destroyDeleteLayerButton();
            this.destroyCreateLayerButton();
        }
        this.destroyExportButtons();
        this.destroyImportButtons();
        this.destroyPixelCanvases(layers);
        this.destroyToolsView(this.pixelInstance.tools.getAllTools());
        this.destroyLockedLayerSelectors(background);
        this.destroyDownloadLinks();
        this.destroyBrushCursor();
        this.restoreDefaultCursor();
    }

    // Tools are strings or enums
    createToolsView (tools)
    {
        let form = document.createElement("form");
        form.setAttribute("id", "tool-selector");
        form.setAttribute("class", "tool-selector");

        let handleClick = (radio) =>
        {
            radio.addEventListener("click", () =>
            {
                this.pixelInstance.tools.setCurrentTool(radio.value);
            });
        };

        // Create an element for each tool and
        for (let index = 0; index < tools.length; index++)
        {
            let tool = tools[index],
                radio = document.createElement("input"),
                //content = document.createTextNode(tool),
                content = document.createElement("label");

            content.setAttribute("for", tool);
            content.innerHTML = tool;

            radio.setAttribute("id", tool);
            radio.setAttribute("type", "radio");
            radio.setAttribute("value", tool);
            radio.setAttribute("name", "tool-selector");
            radio.setAttribute("class", "radio-select");
            handleClick(radio);

            form.appendChild(radio);
            form.appendChild(content);
        }
        document.body.appendChild(form);
        // Set tool cursor after tools view creation
        this.pixelInstance.tools.setCurrentTool(this.pixelInstance.tools.getCurrentTool());
    }

    destroyToolsView ()
    {
        let form = document.getElementById("tool-selector");
        form.parentNode.removeChild(form);
    }

    placeLayerCanvasesInDiva (layers)
    {
        let divaCanvas = this.pixelInstance.core.getSettings().renderer._canvas;
        for (let index = layers.length - 1; index >= 0; index--)
        {
            let layer = layers[index];
            layer.placeCanvasAfterElement(divaCanvas);

            if (layer.isActivated())
                layer.getCanvas().style.opacity = layer.getLayerOpacity();
            else
                layer.getCanvas().style.opacity = 0;
        }

        if (this.pixelInstance.background.isActivated())
            this.pixelInstance.background.getCanvas().style.opacity = this.pixelInstance.background.getLayerOpacity();
        else
            this.pixelInstance.background.getCanvas().style.opacity = 0;
    }

    destroyPixelCanvases (layers)
    {
        layers.forEach ((layer) =>
        {
            if (layer.getCanvas().parentNode !== null)
                layer.getCanvas().parentNode.removeChild(layer.getCanvas());
        });
    }

    createOpacitySlider (layer, parentElement, referenceNode)
    {
        let br = document.createElement("br"),
            opacityDiv = document.createElement("div"),
            opacityText = document.createElement("p"),
            opacitySlider = document.createElement("input"),
            text = document.createTextNode("Opacity");

        br.setAttribute("id", "opacity-br-" + layer.layerId);

        opacityDiv.setAttribute("class", "layer-tool");
        opacityDiv.setAttribute("id", "layer-" + layer.layerId + "-opacity-tool");

        opacityText.setAttribute("class", "layer-tool-text");
        opacityText.setAttribute("id", "layer-" + layer.layerId + "-opacity-text");

        opacitySlider.setAttribute("class", "layer-tool-slider");
        opacitySlider.setAttribute("id", "layer-" + layer.layerId + "-opacity-slider");
        opacitySlider.setAttribute("type", "range");
        opacitySlider.setAttribute('max', 50);
        opacitySlider.setAttribute('min', 0);

        opacitySlider.setAttribute('value', layer.getLayerOpacity() * 50);
        opacitySlider.setAttribute("draggable", "false");

        opacitySlider.addEventListener("input", () =>
        {
            layer.setLayerOpacity(opacitySlider.value / 50);
            if (layer.isActivated())    // Re-specify opacity only when the layer is activated
                layer.getCanvas().style.opacity = layer.getLayerOpacity();
        });

        opacityText.appendChild(text);
        opacityDiv.appendChild(opacityText);
        opacityDiv.appendChild(opacitySlider);
        parentElement.insertBefore(opacityDiv, referenceNode.nextSibling);
        parentElement.insertBefore(br, referenceNode.nextSibling);
    }

    destroyOpacitySlider (layer)
    {
        let opacitySlider = document.getElementById("layer-" + layer.layerId + "-opacity-tool"),
            br = document.getElementById("opacity-br-" + layer.layerId);
        opacitySlider.parentElement.removeChild(opacitySlider);
        br.parentElement.removeChild(br);
    }

    createBackground ()
    {
        let backgroundViewDiv = document.createElement("div");
        backgroundViewDiv.setAttribute("id", "background-view");
        backgroundViewDiv.setAttribute("class", "background-view");

        // Should only have 1 element, but perhaps there will one day be more than 1 background
        let layer = this.pixelInstance.background,
            layerDiv = document.createElement("div"),
            colourDiv = document.createElement("div"),
            layerName = document.createElement("input"),
            layerOptionsDiv = document.createElement("div"),
            layerActivationDiv = document.createElement("div");

        layerDiv.setAttribute("draggable", "false");
        layerDiv.setAttribute("class", "layer-div");
        layerDiv.setAttribute("value", layer.layerId);
        layerDiv.setAttribute("id", "layer-" + layer.layerId + "-selector");

        layerName.setAttribute("type", "text");
        layerName.setAttribute("readonly", "true");
        layerName.setAttribute("value", layer.layerName);

        colourDiv.setAttribute("class", "color-box");
        colourDiv.setAttribute("style", "background-color: " + layer.colour.toHexString() + ";");

        layerOptionsDiv.setAttribute("class", "unchecked-layer-settings");
        layerOptionsDiv.setAttribute("id", "layer-" + layer.layerId + "-options");

        if (this.pixelInstance.background.isActivated())
        {
            layerActivationDiv.setAttribute("class", "layer-activated");
            this.pixelInstance.background.getCanvas().style.opacity = 1;
        }
        else
        {
            layerActivationDiv.setAttribute("class", "layer-deactivated");
            this.pixelInstance.background.getCanvas().style.opacity = 0;
        }

        layerActivationDiv.setAttribute("id", "layer-" + layer.layerId + "-activation");

        colourDiv.addEventListener("click", () => { layer.displayColourOptions(); });
        layerActivationDiv.addEventListener("click", () => { layer.toggleLayerActivation(); });
        layerOptionsDiv.onclick = () => { layer.displayLayerOptions(); };

        layerDiv.appendChild(layerName);
        layerDiv.appendChild(layerOptionsDiv);
        layerDiv.appendChild(colourDiv);
        layerDiv.appendChild(layerActivationDiv);
        backgroundViewDiv.appendChild(layerDiv);

        document.body.appendChild(backgroundViewDiv);
    }

    destroyLockedLayerSelectors ()
    {
        let backgroundViewDiv = document.getElementById("background-view");
        backgroundViewDiv.parentNode.removeChild(backgroundViewDiv);
    }

    createLayersView (layers)
    {
        let departureIndex, destinationIndex,
            duringSwap = false;

        let layersViewDiv = document.createElement("div");
        layersViewDiv.setAttribute("id", "layers-view");
        layersViewDiv.setAttribute("class", "layers-view");

        let handleEvents = (layer, colourDiv, layerActivationDiv, layerName, layerOptionsDiv, layerDiv) =>
        {
            colourDiv.addEventListener("click", () => { layer.displayColourOptions(); });
            layerActivationDiv.addEventListener("click", () => { layer.toggleLayerActivation(); });
            layerName.addEventListener('keypress', (e) => { this.pixelInstance.editLayerName(e, layerName, layerDiv, false, duringSwap, layer); });
            layerOptionsDiv.onclick = () => { layer.displayLayerOptions(); };

            layerDiv.ondrag = (evt) =>
            {
                this.pixelInstance.dragging(evt);
                duringSwap = true;
            };
            layerDiv.ondragstart = (evt) => { this.pixelInstance.dragStart(evt); };
            layerDiv.ondrop = (evt) => {
                this.pixelInstance.drop(evt, departureIndex, destinationIndex);
                duringSwap = false;
            };
            layerDiv.onmousedown = () =>
            {
                departureIndex = layerDiv.getAttribute("index");
                this.highlightLayerSelectorById(layer.layerId);
            };

            layerDiv.ondragover = (evt) =>
            {
                this.pixelInstance.allowDrop(evt);
                destinationIndex = layerDiv.getAttribute("index");
            };
        };

        // Backwards because layers' display should be the same as the layers' order/visual "z-index" priority (depth)
        for (var index = layers.length - 1; index >= 0; index--)
        {
            let layer = layers[index],
                layerDiv = document.createElement("div"),
                linebreak = document.createElement("br"),
                colourDiv = document.createElement("div"),
                layerName = document.createElement("input"),
                layerOptionsDiv = document.createElement("div"),
                layerActivationDiv = document.createElement("div");

            layerDiv.setAttribute("index", index);
            layerDiv.setAttribute("draggable", "true");
            layerDiv.setAttribute("class", "layer-div");
            layerDiv.setAttribute("value", layer.layerId);
            layerDiv.setAttribute("id", "layer-" + layer.layerId + "-selector");
            layerDiv.setAttribute("title", "Hotkey: " + layer.layerId);
            layerName.setAttribute("type", "text");
            layerName.setAttribute("readonly", "true");
            layerName.setAttribute("value", layer.layerName);
            layerName.setAttribute("ondblclick", "this.readOnly='';");

            //sets draggable attribute to false on double click
            //only allows the onblur event after a double click
            layerName.addEventListener('dblclick', (e) => { // jshint ignore:line
                this.pixelInstance.editLayerName(e, layerName, layerDiv, false, duringSwap, layer);
                layerName.onblur = (e) => {
                    this.pixelInstance.editLayerName(e, layerName, layerDiv, true, duringSwap, layer);
                };
            });

            colourDiv.setAttribute("class", "color-box");
            colourDiv.setAttribute("style", "background-color: " + layer.colour.toHexString() + ";");

            layerOptionsDiv.setAttribute("class", "unchecked-layer-settings");
            layerOptionsDiv.setAttribute("id", "layer-" + layer.layerId + "-options");

            if (layer.isActivated())
            {
                layerActivationDiv.setAttribute("class", "layer-activated");
            }
            else
            {
                layerActivationDiv.setAttribute("class", "layer-deactivated");
            }

            layerActivationDiv.setAttribute("id", "layer-" + layer.layerId + "-activation");

            if (layer.layerId === this.pixelInstance.layers[this.pixelInstance.selectedLayerIndex].layerId)
            {
                layerDiv.classList.add("selected-layer");
            }

            handleEvents(layer, colourDiv, layerActivationDiv, layerName, layerOptionsDiv, layerDiv);

            layerDiv.appendChild(layerName);
            layerDiv.appendChild(layerOptionsDiv);
            layerDiv.appendChild(colourDiv);
            layerDiv.appendChild(layerActivationDiv);
            layersViewDiv.appendChild(layerDiv);
            layersViewDiv.appendChild(linebreak);
        }
        document.body.appendChild(layersViewDiv);

        this.createBackground(layers);

    }

    destroyLayerSelectors ()
    {
        let layersViewDiv = document.getElementById("layers-view");
        layersViewDiv.parentNode.removeChild(layersViewDiv);
    }

    highlightLayerSelectorById (layerToHighlightId)
    {
        let matchFound = false;

        this.pixelInstance.layers.forEach((layer) =>
        {
            if (layer.layerId === layerToHighlightId)
            {
                matchFound = true;
            }
        });

        if (!matchFound)
        {
            throw new CannotSelectLayerException("The layer you are trying to select does not exist.");
        }

        this.pixelInstance.layers.forEach ((layer) =>
        {
            // Highlight only the selected layer and remove highlights from all other layers
            if (layer.layerId === layerToHighlightId)
            {
                let div = document.getElementById("layer-" + layer.layerId + "-selector");

                if (!div.hasAttribute("selected-layer"))
                    div.classList.add("selected-layer");
                this.pixelInstance.changeCurrentlySelectedLayerIndex(this.pixelInstance.layers.indexOf(layer));
            }
            else
            {
                let div = document.getElementById("layer-" + layer.layerId + "-selector");
                if (div.classList.contains("selected-layer"))
                    div.classList.remove("selected-layer");
            }
        });
    }

    createBrushSizeSelector ()
    {
        let brushSizeDiv = document.createElement("div");
        brushSizeDiv.setAttribute("class", "tool-settings");
        brushSizeDiv.setAttribute("id", "brush-size");

        let text = document.createTextNode("Brush size:"),
            brushSizeSelector = document.createElement("input");

        brushSizeSelector.setAttribute("id", "brush-size-selector");
        brushSizeSelector.setAttribute("type", "range");
        brushSizeSelector.setAttribute('max', 40);
        brushSizeSelector.setAttribute('min', 1);
        brushSizeSelector.setAttribute('value', 25);

        brushSizeSelector.addEventListener("input", () =>
        {
            this.createBrushCursor();
        });

        brushSizeDiv.appendChild(text);
        brushSizeDiv.appendChild(brushSizeSelector);
        document.body.appendChild(brushSizeDiv);
    }

    destroyBrushSizeSelector ()
    {
        let brushSizeDiv = document.getElementById("brush-size");
        if (brushSizeDiv !== null)
            brushSizeDiv.parentNode.removeChild(brushSizeDiv);
    }

    createUndoButton ()
    {
        let undoButton = document.createElement("button"),
            text = document.createTextNode("Undo");

        this.undo = () => { this.pixelInstance.undoAction(); };

        undoButton.setAttribute("id", "undo-button");
        undoButton.appendChild(text);
        undoButton.addEventListener("click", this.undo);

        document.body.appendChild(undoButton);
    }

    destroyUndoButton ()
    {
        let undoButton = document.getElementById("undo-button");
        undoButton.parentNode.removeChild(undoButton);
    }

    createRedoButton ()
    {
        let redoButton = document.createElement("button"),
            text = document.createTextNode("Redo");

        this.redo = () => { this.pixelInstance.redoAction(); };

        redoButton.setAttribute("id", "redo-button");
        redoButton.appendChild(text);
        redoButton.addEventListener("click", this.redo);

        document.body.appendChild(redoButton);
    }

    destroyRedoButton ()
    {
        let redoButton = document.getElementById("redo-button");
        redoButton.parentNode.removeChild(redoButton);
    }

    createDeleteLayerButton ()
    {
        let deleteLayerButton = document.createElement("button"),
            text = document.createTextNode("Delete selected layer");

        this.deleteLayer = () =>
        {
            try
            {
                this.pixelInstance.deleteLayer();
            }
            catch (e)
            {
                if (e instanceof CannotDeleteLayerException)
                {
                    alert(e.message);
                }
            }
        };

        deleteLayerButton.setAttribute("id", "delete-layer-button");
        deleteLayerButton.appendChild(text);
        deleteLayerButton.addEventListener("click", this.deleteLayer);

        document.body.appendChild(deleteLayerButton);
    }

    destroyDeleteLayerButton ()
    {
        let deleteLayerButton = document.getElementById("delete-layer-button");
        deleteLayerButton.parentNode.removeChild(deleteLayerButton);
    }

    createCreateLayerButton ()
    {
        let createLayerButton = document.createElement("button"),
            text = document.createTextNode("Create new layer");

        this.createLayer = () => { this.pixelInstance.createLayer(); };

        createLayerButton.setAttribute("id", "create-layer-button");
        createLayerButton.appendChild(text);
        createLayerButton.addEventListener("click", this.createLayer);

        document.body.appendChild(createLayerButton);
    }

    destroyCreateLayerButton ()
    {
        let createLayerButton = document.getElementById("create-layer-button");
        createLayerButton.parentNode.removeChild(createLayerButton);
    }

    createExportButtons ()
    {
        let csvExportButton = document.createElement("button"),
            csvExportText = document.createTextNode("Export as CSV"),
            pngExportButton = document.createElement("button"),
            pngExportText = document.createTextNode("Export as PNG"),
            pngDataExportButton = document.createElement("button"),
            pngDataExportText = document.createTextNode("Export as image Data PNG");

        this.exportCSV = () => { this.pixelInstance.exportAsCSV(); };
        this.exportPNG = () => { this.pixelInstance.exportAsPNG(); };
        this.exportPNGData = () => { this.pixelInstance.exportAsImageData(); };

        csvExportButton.setAttribute("id", "csv-export-button");
        csvExportButton.appendChild(csvExportText);
        csvExportButton.addEventListener("click", this.exportCSV);

        pngExportButton.setAttribute("id", "png-export-button");
        pngExportButton.appendChild(pngExportText);
        pngExportButton.addEventListener("click", this.exportPNG);

        pngDataExportButton.setAttribute("id", "png-export-data-button");
        pngDataExportButton.appendChild(pngDataExportText);
        pngDataExportButton.addEventListener("click", this.exportPNGData);

        document.body.appendChild(csvExportButton);
        document.body.appendChild(pngExportButton);
        document.body.appendChild(pngDataExportButton);
    }

    destroyExportButtons ()
    {
        let csvexportButton = document.getElementById("csv-export-button"),
            pngexportButton = document.getElementById("png-export-button"),
            pngexportDataButton = document.getElementById("png-export-data-button");

        csvexportButton.parentNode.removeChild(csvexportButton);
        pngexportButton.parentNode.removeChild(pngexportButton);
        pngexportDataButton.parentNode.removeChild(pngexportDataButton);
    }


    createImportButtons ()
    {
        let imageLoader = document.createElement("input");
        imageLoader.setAttribute("type", "file");
        imageLoader.setAttribute("id", "imageLoader");
        imageLoader.setAttribute("name", "imageLoader");

        this.import = (e) => { this.pixelInstance.importPNGToLayer(e); };

        imageLoader.addEventListener('change', this.import, false);

        document.body.appendChild(imageLoader);
    }

    destroyImportButtons ()
    {
        let imageLoader = document.getElementById("imageLoader");
        imageLoader.parentNode.removeChild(imageLoader);
    }

    updateProgress (percentage)
    {
        let percentageStr = percentage + "%",
            widthStr = "width: " + percentageStr;

        document.getElementById("pbar-inner-div").setAttribute("style", widthStr);
        document.getElementById("pbar-inner-text").innerHTML = percentageStr;
    }

    destroyBackground (layers)
    {
        this.pixelInstance.destroyLockedLayerSelectors(layers);
    }

    createExportElements (exportInstance)
    {
        let exportDiv = document.createElement('div'),
            text = document.createTextNode("Exporting"),
            progressText = document.createTextNode("0%"),
            progressBarOuterDiv = document.createElement('div'),
            progressBarInnerDiv = document.createElement('div'),
            progressBarInnerText = document.createElement('div'),
            progressBarExportText = document.createElement('div'),
            cancelExportDiv = document.createElement('div'),
            cancelExportText = document.createTextNode("Cancel");

        exportDiv.setAttribute("class", "export-div");
        exportDiv.setAttribute("id", "pixel-export-div");

        progressBarOuterDiv.setAttribute("class", "pbar-outer-div");
        progressBarOuterDiv.setAttribute("id", "pbar-outer-div");

        progressBarInnerDiv.setAttribute("class", "pbar-inner-div");
        progressBarInnerDiv.setAttribute("id", "pbar-inner-div");

        progressBarInnerText.setAttribute("class", "pbar-inner-text");
        progressBarInnerText.setAttribute("id", "pbar-inner-text");

        progressBarExportText.setAttribute("class", "pbar-export-text");
        progressBarExportText.setAttribute("id", "pbar-export-text");

        cancelExportDiv.setAttribute("class", "cancel-export-div");
        cancelExportDiv.setAttribute("id", "cancel-export-div");
        cancelExportDiv.addEventListener("click", () =>
        {
            cancelExportDiv.setAttribute("style", "background-color: #AAAAAA;");
            exportInstance.exportInterrupted = true;
        });

        progressBarExportText.appendChild(text);
        cancelExportDiv.appendChild(cancelExportText);
        progressBarInnerText.appendChild(progressText);
        progressBarOuterDiv.appendChild(progressBarInnerDiv);
        progressBarOuterDiv.appendChild(progressBarInnerText);
        progressBarOuterDiv.appendChild(progressBarExportText);
        progressBarOuterDiv.appendChild(cancelExportDiv);
        exportDiv.appendChild(progressBarOuterDiv);

        document.body.appendChild(exportDiv);

        return {
            progressCanvas: this.createProgressCanvas(exportInstance.pageIndex, exportInstance.zoomLevel)
        };
    }

    destroyExportElements ()
    {
        let exportDiv = document.getElementById("pixel-export-div");
        exportDiv.parentNode.removeChild(exportDiv);
    }

    destroyDownloadLinks ()
    {
        let downloadElements = document.getElementsByClassName("export-download");

        while (downloadElements[0])
        {
            downloadElements[0].parentNode.removeChild(downloadElements[0]);
        }
    }

    createProgressCanvas (pageIndex, zoomLevel)
    {
        let height = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(pageIndex, zoomLevel).height,
            width = this.pixelInstance.core.publicInstance.getPageDimensionsAtZoomLevel(pageIndex, zoomLevel).width;

        let progressCanvas = document.createElement('canvas');
        progressCanvas.setAttribute("id", "progress-canvas");
        progressCanvas.style.opacity = 0.3;
        progressCanvas.width = width;
        progressCanvas.height = height;
        progressCanvas.globalAlpha = 1;

        let w = window,
            d = document,
            e = d.documentElement,
            g = d.getElementsByTagName('body')[0],
            y = w.innerHeight|| e.clientHeight|| g.clientHeight;

        progressCanvas.style.height = y + "px";

        let exportDiv = document.getElementById("pixel-export-div");
        exportDiv.appendChild(progressCanvas);

        return progressCanvas;
    }

    markToolSelected (tool)
    {
        document.getElementById(tool).checked = true;
    }

    getBrushSizeSelectorValue ()
    {
        // Brush size relative to scaleRatio to allow for more precise manipulations on higher zoom levels
        let brushSizeSlider = document.getElementById("brush-size-selector"),
            brushSizeValue = (brushSizeSlider.value / brushSizeSlider.max) * 10;

        return 0.05 + Math.exp(brushSizeValue - 6);   // 0.05 + e ^ (x - 6) was the most intuitive function we found in terms of brush size range
    }

    createBrushCursor ()
    {
        let cursorDiv = document.getElementById("brush-cursor-div"),
            divaViewport = document.getElementById("diva-1-viewport"),
            divaOuter = document.getElementById("diva-1-outer");

        if (cursorDiv === null)
        {
            cursorDiv = document.createElement('div');
            cursorDiv.setAttribute("id", "brush-cursor-div");
            divaOuter.insertBefore(cursorDiv, divaViewport);
        }

        cursorDiv.setAttribute("oncontextmenu", "return false");
        this.resizeBrushCursor();
    }

    resizeBrushCursor ()
    {
        let cursorDiv = document.getElementById("brush-cursor-div");

        if (cursorDiv === null)
            return;

        let scaleRatio = Math.pow(2, this.pixelInstance.core.getSettings().zoomLevel),
            brushSizeSelectorValue = this.getBrushSizeSelectorValue() * scaleRatio;

        cursorDiv.style.width = brushSizeSelectorValue + "px";
        cursorDiv.style.height = brushSizeSelectorValue + "px";
    }

    destroyBrushCursor ()
    {
        let cursorDiv = document.getElementById("brush-cursor-div");

        if (cursorDiv !== null)
        {
            cursorDiv.parentNode.removeChild(cursorDiv);
        }
    }

    moveBrushCursor (mousePos)
    {
        let cursorDiv = document.getElementById("brush-cursor-div"),
            scaleRatio = Math.pow(2, this.pixelInstance.core.getSettings().zoomLevel),
            brushSize = this.getBrushSizeSelectorValue() * scaleRatio;

        cursorDiv.style.left = mousePos.x - brushSize/2 - 1 + "px"; // the -1 is to account for the border width
        cursorDiv.style.top = mousePos.y  - brushSize/2 - 1 + "px"; // the -1 is to account for the border width
    }

    restoreDefaultCursor ()
    {
        let mouseClickDiv = document.getElementById("diva-1-outer");
        mouseClickDiv.style.cursor = "default";
    }

    setMousePosition (mousePos)
    {
        // Rectangle border width
        let borderWidth = 1;

        this.mouse.x = mousePos.x - borderWidth;
        this.mouse.y = mousePos.y - borderWidth;
    }

    createRectanglePreview (mousePos, layer)
    {
        this.setMousePosition(mousePos);

        let divaViewport = document.getElementById("diva-1-viewport");
        let divaOuter = document.getElementById("diva-1-outer");

        this.mouse.startX = this.mouse.x;
        this.mouse.startY = this.mouse.y;
        let element = document.createElement('div');
        element.className = 'rectangle';
        element.id = 'preview-rectangle';
        element.style.left = this.mouse.x + 'px';
        element.style.top = this.mouse.y + 'px';
        element.style.border = "1px solid " + layer.colour.toHexString();

        divaOuter.insertBefore(element, divaViewport);
    }

    resizeRectanglePreview (mousePos, layer)
    {
        this.setMousePosition(mousePos);
        let element = document.getElementById("preview-rectangle");

        if (element !== null)
        {
            element.style.border = "1px solid " + layer.colour.toHexString();
            element.style.width = Math.abs(this.mouse.x - this.mouse.startX) + 'px';
            element.style.height = Math.abs(this.mouse.y - this.mouse.startY) + 'px';
            element.style.left = (this.mouse.x - this.mouse.startX < 0) ? this.mouse.x + 'px' : this.mouse.startX + 'px';
            element.style.top = (this.mouse.y - this.mouse.startY < 0) ? this.mouse.y + 'px' : this.mouse.startY + 'px';
        }
    }

    removeRectanglePreview ()
    {
        let element = document.getElementById("preview-rectangle");
        if (element !== null)
            element.parentNode.removeChild(element);
    }

    isInPageBounds (relativeX, relativeY)
    {
        let pageIndex = this.pixelInstance.core.getSettings().currentPageIndex,
            zoomLevel = this.pixelInstance.core.getSettings().zoomLevel,
            renderer  = this.pixelInstance.core.getSettings().renderer;

        let pageDimensions = this.pixelInstance.core.publicInstance.getCurrentPageDimensionsAtCurrentZoomLevel(),
            absolutePageOrigin = new Point().getCoordsInViewport(zoomLevel,pageIndex,renderer),
            absolutePageWidthOffset = pageDimensions.width + absolutePageOrigin.x,  //Taking into account the padding, etc...
            absolutePageHeightOffset = pageDimensions.height + absolutePageOrigin.y,
            relativeBounds = new Point().getRelativeCoordinatesFromPadded(pageIndex, renderer, absolutePageWidthOffset, absolutePageHeightOffset, zoomLevel);

        if (relativeX < 0 || relativeY < 0 || relativeX > relativeBounds.x || relativeY > relativeBounds.y)
            return false;

        return true;
    }

    /**
     * ===============================================
     *                     Tutorial
     * ===============================================
     **/

    tutorial ()
    {
        let overlay = document.createElement('div');
        overlay.setAttribute("id", "tutorial-div");

        let background = document.createElement('div');
        background.setAttribute("id", "tutorial-overlay");

        let modal = document.createElement('div');
        modal.setAttribute("id", "myModal");
        modal.setAttribute("class", "modal");

        let modalContent = document.createElement('div');
        modalContent.setAttribute("class", "modal-content");

        let modalHeader = document.createElement('div');
        modalHeader.setAttribute("class", "modal-header");

        let text = document.createTextNode("Hello, World");
        let h2 = document.createElement('h2');
        h2.appendChild(text);

        let closeModal = document.createElement('span');
        closeModal.setAttribute("class", "close");
        closeModal.innerHTML = "&times;";

        let modalBody = document.createElement('div');
        modalBody.setAttribute("class", "modal-body");

        let tutorialP = document.createElement('p');
        tutorialP.innerHTML = "The following is a glossary of the hotkeys you will find useful when using Pixel.js";

        let hotkeyGlossary = document.createElement('ul');
        hotkeyGlossary.setAttribute("style", "list-style-type:none;");

        let LayerSelect = document.createElement('li');
        LayerSelect.innerHTML = "<kbd>1</kbd> ... <kbd>9</kbd> layer select";

        let brushTool = document.createElement('li');
        brushTool.innerHTML = "<kbd>b</kbd> brush tool";

        let rectangleTool = document.createElement('li');
        rectangleTool.innerHTML = "<kbd>r</kbd> rectangle tool";

        let grabTool = document.createElement('li');
        grabTool.innerHTML = "<kbd>g</kbd> grab tool";

        let eraserTool = document.createElement('li');
        eraserTool.innerHTML = "<kbd>e</kbd> eraser tool";

        let shift = document.createElement('li');
        shift.innerHTML = "<kbd>Shift</kbd>  force tools to paint in an exact way.";

        let undo = document.createElement('li');
        undo.innerHTML = "<kbd>cmd</kbd> + <kbd>z</kbd> undo";

        let redo = document.createElement('li');
        redo.innerHTML = "<kbd>cmd</kbd> + <kbd>Shift</kbd> + <kbd>z</kbd> redo";

        let modalFooter = document.createElement('div');
        modalFooter.setAttribute("class", "modal-footer");

        let close = document.createElement('h2');
        close.innerHTML = "Got It!";

        hotkeyGlossary.appendChild(LayerSelect);
        hotkeyGlossary.appendChild(brushTool);
        hotkeyGlossary.appendChild(rectangleTool);
        hotkeyGlossary.appendChild(grabTool);
        hotkeyGlossary.appendChild(eraserTool);
        hotkeyGlossary.appendChild(shift);
        hotkeyGlossary.appendChild(undo);
        hotkeyGlossary.appendChild(redo);

        modal.appendChild(modalContent);
        modalContent.appendChild(modalHeader);
        modalContent.appendChild(modalBody);
        modalContent.appendChild(modalFooter);
        modalHeader.appendChild(h2);
        modalHeader.appendChild(closeModal);
        modalBody.appendChild(tutorialP);
        modalBody.appendChild(hotkeyGlossary);
        modalFooter.appendChild(close);

        overlay.appendChild(background);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        modal.style.display = "block";

        modalFooter.addEventListener("click", () =>
        {
            overlay.parentNode.removeChild(overlay);
        });
    }
}
