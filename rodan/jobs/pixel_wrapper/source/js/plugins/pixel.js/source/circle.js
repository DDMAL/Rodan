/*jshint esversion: 6 */
import {Shape} from './shape';
import {Point} from './point';
import {Colour} from './colour';

export class Circle extends Shape
{
    constructor (point, relativeRadius, blendMode)
    {
        super(point, blendMode);
        this.relativeRadius = relativeRadius;
    }

    /**
     * draws a circle of a certain layer in a canvas using viewport coordinates (padded coordinates)
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

        if (pageIndex === this.origin.pageIndex)
        {
            // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
            // (to make it look like it is on top of a page in Diva)
            let absoluteCenterWithPadding = this.origin.getCoordsInViewport(zoomLevel, pageIndex, renderer);

            //Draw the circle
            ctx.fillStyle = layer.colour.toHTMLColour();
            ctx.beginPath();
            ctx.arc(absoluteCenterWithPadding.x,absoluteCenterWithPadding.y, this.relativeRadius * scaleRatio,0,2*Math.PI);
            ctx.fill();
        }
    }

    /**
     * draws a circle of a certain layer in a canvas using absolute page coordinates
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

        if (pageIndex === this.origin.pageIndex)
        {
            // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
            // (to make it look like it is on top of a page in Diva)
            let absoluteCenter = this.origin.getCoordsInPage(zoomLevel);

            //Draw the circle
            ctx.fillStyle = layer.colour.toHTMLColour();
            ctx.beginPath();
            ctx.arc(absoluteCenter.x,absoluteCenter.y, this.relativeRadius * scaleRatio,0,2*Math.PI);
            ctx.fill();
        }
    }

    /**
     * Gets all the pixels spanned by a circle. Draws the image data that the circle covers (from the imageCanvas) in the drawingCanvas
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param drawingCanvas
     * @param imageCanvas
     */
    getPixels (layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas)
    {
        let circleTop = new Point(this.origin.relativeOriginX, this.origin.relativeOriginY - this.relativeRadius, 0),
            circleBottom = new Point(this.origin.relativeOriginX, this.origin.relativeOriginY + this.relativeRadius, 0),
            circleLeft = new Point(this.origin.relativeOriginX - this.relativeRadius, this.origin.relativeOriginY, 0),
            circleRight = new Point(this.origin.relativeOriginX + this.relativeRadius, this.origin.relativeOriginY, 0);

        let drawingCtx = drawingCanvas.getContext('2d'),
            imageCtx = imageCanvas.getContext('2d');

        let scaleRatio = Math.pow(2, zoomLevel);

        // Scan a square spanning the top, bottom, left and right coordinates of the circle
        for (var y = circleTop.getCoordsInViewport(zoomLevel, pageIndex, renderer).y;
            y <= circleBottom.getCoordsInViewport(zoomLevel, pageIndex, renderer).y; y++)
        {
            for (var x = circleLeft.getCoordsInViewport(zoomLevel, pageIndex, renderer).x;
                x <= circleRight.getCoordsInViewport(zoomLevel, pageIndex, renderer).x; x++)
            {
                let point1highlightOffset = this.origin.getCoordsInViewport(zoomLevel, pageIndex, renderer);

                let shiftedX = x - point1highlightOffset.x,
                    shiftedY = y - point1highlightOffset.y;

                // If it satisfies the circle equation x^2 + y^2 <= r^2
                if (shiftedX * shiftedX + shiftedY * shiftedY <= (this.relativeRadius) * scaleRatio * (this.relativeRadius) * scaleRatio)
                {
                    // Get absolute from padded
                    let absoluteCoords = new Point().getAbsoluteCoordinatesFromPadded(pageIndex,renderer,x,y);

                    // In bounds
                    if (absoluteCoords.y >= 0 && absoluteCoords.x >= 0 && absoluteCoords.y <= drawingCanvas.height && absoluteCoords.x <= drawingCanvas.width)
                    {
                        if (this.blendMode === "add")
                        {
                            let paddedCoords = new Point().getPaddedCoordinatesFromAbsolute(pageIndex, renderer, absoluteCoords.x, absoluteCoords.y),
                                data = imageCtx.getImageData(paddedCoords.x, paddedCoords.y, 1, 1).data,
                                colour = new Colour(data[0], data[1], data[2], data[3]);

                            drawingCtx.fillStyle = colour.toHTMLColour();
                            drawingCtx.fillRect(absoluteCoords.x, absoluteCoords.y, 1, 1);
                        }

                        else if (this.blendMode === "subtract")
                        {
                            drawingCtx.clearRect(absoluteCoords.x, absoluteCoords.y, 1, 1);
                        }
                    }
                }
            }
        }
    }
}