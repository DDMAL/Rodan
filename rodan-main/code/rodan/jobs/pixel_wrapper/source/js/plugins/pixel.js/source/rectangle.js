/*jshint esversion: 6 */
import {Shape} from './shape';
import {Colour} from './colour';
import {Point} from './point';

export class Rectangle extends Shape
{
    constructor (point, relativeRectWidth, relativeRectHeight, blendMode)
    {
        super(point, blendMode);
        this.relativeRectWidth = relativeRectWidth;
        this.relativeRectHeight = relativeRectHeight;
    }

    /**
     * draws a rectangle of a certain layer in a canvas using viewport coordinates (padded coordinates)
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param canvas
     */
    drawInViewport (layer, pageIndex, zoomLevel, renderer, canvas)
    {
        let scaleRatio = Math.pow(2,zoomLevel),
            ctx = canvas.getContext('2d');

        const viewportPaddingX = Math.max(0, (renderer._viewport.width - renderer.layout.dimensions.width) / 2);
        const viewportPaddingY = Math.max(0, (renderer._viewport.height - renderer.layout.dimensions.height) / 2);

        // The following absolute values are experimental values to highlight the square on the first page of Salzinnes, CDN-Hsmu M2149.L4
        // The relative values are used to scale the highlights according to the zoom level on the page itself
        let absoluteRectOriginX = this.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.relativeRectHeight * scaleRatio;

        //Selection tool
        if (this.blendMode === "select")
        {
            //TODO: SELECTION CODE HERE
            if (pageIndex === this.origin.pageIndex)
            {
                // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
                // (to make it look like it is on top of a page in Diva)
                let highlightXOffset = renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX + absoluteRectOriginX,
                    highlightYOffset = renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY + absoluteRectOriginY;

                //Draw the selection rectangle
                ctx.fillStyle = 'rgba(147, 192, 255, 0.3)';
                ctx.lineWidth = 1;
                ctx.strokeStyle = 'rgba(25, 25, 25, 1)';
                ctx.fillRect(highlightXOffset, highlightYOffset, absoluteRectWidth, absoluteRectHeight);
                ctx.strokeRect(highlightXOffset, highlightYOffset, absoluteRectWidth, absoluteRectHeight);

            }
            return;
        }


        //Rectangle tool
        // TODO: Use padded coordinates
        if (this.blendMode === "add")
        {
            if (pageIndex === this.origin.pageIndex)
            {
                // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
                // (to make it look like it is on top of a page in Diva)
                let highlightXOffset = renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX + absoluteRectOriginX,
                    highlightYOffset = renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY + absoluteRectOriginY;

                //Draw the rectangle
                ctx.fillStyle = layer.colour.toHTMLColour();
                ctx.fillRect(highlightXOffset, highlightYOffset, absoluteRectWidth, absoluteRectHeight);
            }
        }

        else if (this.blendMode === "subtract")
        {
            if (pageIndex === this.origin.pageIndex)
            {
                // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
                // (to make it look like it is on top of a page in Diva)
                let highlightXOffset = renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX + absoluteRectOriginX,
                    highlightYOffset = renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY + absoluteRectOriginY;

                //Draw the rectangle
                ctx.fillStyle = layer.colour.toHTMLColour();
                ctx.clearRect(highlightXOffset, highlightYOffset, absoluteRectWidth, absoluteRectHeight);
            }
        }
    }

    /**
     * draws a rectangle of a certain layer in a canvas using absolute page coordinates
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param canvas
     */
    drawOnPage (layer, pageIndex, zoomLevel, renderer, canvas)
    {
        let scaleRatio = Math.pow(2,zoomLevel),
            ctx = canvas.getContext('2d');

        // The following absolute values are experimental values to highlight the square on the first page of Salzinnes, CDN-Hsmu M2149.L4
        // The relative values are used to scale the highlights according to the zoom level on the page itself
        let absoluteRectOriginX = this.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.relativeRectHeight * scaleRatio;

        if (this.blendMode === "select")
        {
            //TODO: SELECTION CODE HERE
            if (pageIndex === this.origin.pageIndex)
            {
                //Draw the selection rectangle
                ctx.fillStyle = 'rgba(147, 192, 255, 0.5)';
                ctx.lineWidth = 30/scaleRatio;
                ctx.strokeStyle = 'rgba(97, 142, 205, 1)';
                ctx.fillRect(absoluteRectOriginX, absoluteRectOriginY, absoluteRectWidth, absoluteRectHeight);
                ctx.strokeRect(absoluteRectOriginX, absoluteRectOriginY, absoluteRectWidth, absoluteRectHeight);
            }
        }

        // TODO: Use padded coordinates
        else if (this.blendMode === "add")
        {
            if (pageIndex === this.origin.pageIndex && layer.layerId === -1) // "Select Region" layer 
            {
                // Draw the rectangle with a border
                ctx.fillStyle = layer.colour.toHTMLColour();
                ctx.lineWidth = 1;
                ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
                ctx.fillRect(absoluteRectOriginX, absoluteRectOriginY, absoluteRectWidth, absoluteRectHeight);
                ctx.strokeRect(absoluteRectOriginX, absoluteRectOriginY, absoluteRectWidth, absoluteRectHeight);
            } else if (pageIndex === this.origin.pageIndex) { 
                // Draw rectangle without border
                ctx.fillStyle = layer.colour.toHTMLColour();
                ctx.fillRect(absoluteRectOriginX, absoluteRectOriginY,absoluteRectWidth,absoluteRectHeight);
            }
        }

        else if (this.blendMode === "subtract")
        {
            if (pageIndex === this.origin.pageIndex)
            {
                //Draw the rectangle
                ctx.fillStyle = layer.colour.toHTMLColour();
                ctx.clearRect(absoluteRectOriginX, absoluteRectOriginY,absoluteRectWidth,absoluteRectHeight);
            }
        }
    }

    /**
     * Gets all the pixels spanned by a rectangle. Draws the image data that the rectangle covers (from the imageCanvas) in the drawingCanvas
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param drawingCanvas
     * @param imageCanvas
     */
    getPixels (layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas)
    {
        // FIXME: sometimes copying and pasting scaled image data goes beyond the rectangle (compute bounds using the scaleRatio)

        let scaleRatio = Math.pow(2,zoomLevel),
            pixelCtx = drawingCanvas.getContext('2d'),
            divaCtx = imageCanvas.getContext('2d');

        // The following absolute values are experimental values to highlight the square on the first page of Salzinnes, CDN-Hsmu M2149.L4
        // The relative values are used to scale the highlights according to the zoom level on the page itself
        let absoluteRectOriginX = this.origin.relativeOriginX * scaleRatio,
            absoluteRectOriginY = this.origin.relativeOriginY * scaleRatio,
            absoluteRectWidth = this.relativeRectWidth * scaleRatio,
            absoluteRectHeight = this.relativeRectHeight * scaleRatio;

        if (pageIndex === this.origin.pageIndex)
        {
            for (var row = Math.round(Math.min(absoluteRectOriginY, absoluteRectOriginY + absoluteRectHeight)); row <  Math.max(absoluteRectOriginY, absoluteRectOriginY + absoluteRectHeight); row++)
            {
                for (var col = Math.round(Math.min(absoluteRectOriginX, absoluteRectOriginX + absoluteRectWidth)); col < Math.max(absoluteRectOriginX, absoluteRectOriginX + absoluteRectWidth); col++)
                {
                    if (row >= 0 && col >= 0 && row < drawingCanvas.height && col < drawingCanvas.width)
                    {
                        if (this.blendMode === "add")
                        {
                            let paddedCoords = new Point().getPaddedCoordinatesFromAbsolute(pageIndex, renderer, col, row),
                                data = divaCtx.getImageData(paddedCoords.x, paddedCoords.y, 1, 1).data,
                                colour = new Colour(data[0], data[1], data[2], data[3]);


                            let maxLevelCol = (col/scaleRatio) * Math.pow(2,5),     // FIXME: Replace with maxZoomLevel
                                maxLevelRow = (row/scaleRatio) * Math.pow(2,5);

                            pixelCtx.fillStyle = colour.toHTMLColour();
                            pixelCtx.fillRect(maxLevelCol, maxLevelRow, Math.pow(2,5), Math.pow(2,5));
                        }

                        else if (this.blendMode === "subtract")
                        {
                            pixelCtx.clearRect(col, row, 1, 1);
                        }
                    }
                }
            }
        }
    }
}
