/*jshint esversion: 6 */
import {Point} from './point';
import {Colour} from './colour';

export class Shape
{
    constructor (point, blendMode)
    {
        this.origin = point;
        this.type = "shape";
        this.blendMode = blendMode;
    }

    /**
     * Abstract method, to be overridden
     */
    drawInViewport ()
    {

    }

    /**
     * Abstract method, to be overridden
     */
    drawOnPage ()
    {

    }

    changeBlendModeTo (newBlendMode)
    {
        this.blendMode = newBlendMode;
    }

    /**
     * Gets all the pixels spanned by a shape given its set of edges. Draws the image data that the shape covers (from the imageCanvas) in the drawingCanvas
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param drawingCanvas
     * @param imageCanvas
     * @param ymax
     * @param ymin
     * @param pairOfEdges
     */
    getPixels (layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas, ymax, ymin, pairOfEdges)
    {
        let drawingCtx = drawingCanvas.getContext('2d'),
            imageCtx = imageCanvas.getContext('2d');

        // TODO: Check for horizontal or vertical lines
        // For every scan line
        for (var y = ymin; y < ymax; y++)
        {
            let intersectionPoints = [];

            // For every line calculate the intersection edges
            for (var e = 0; e < pairOfEdges.length; e++)
            {
                // Calculate intersection with line
                for(var p = 0; p < pairOfEdges[e].length - 1; p++)
                {
                    let x1 = pairOfEdges[e][p].absolutePaddedX,
                        y1 = pairOfEdges[e][p].absolutePaddedY,
                        x2 = pairOfEdges[e][p + 1].absolutePaddedX,
                        y2 = pairOfEdges[e][p + 1].absolutePaddedY;

                    //ctx.fillStyle = layer.colour.toHTMLColour();
                    let deltax = x2 - x1,
                        deltay = y2 - y1;

                    let x = x1 + deltax / deltay * (y - y1),
                        roundedX = Math.round(x);

                    if ((y1 <= y && y2 > y) || (y2 <= y && y1 > y))
                    {
                        intersectionPoints.push({
                            absolutePaddedX: roundedX,
                            absolutePaddedY: y
                        });
                    }
                }
            }

            intersectionPoints.sort((a, b) => {
                return a.absolutePaddedX - b.absolutePaddedX;
            });

            if (intersectionPoints.length <= 0)
                continue;

            // Start filling
            for (var index = 0; index < intersectionPoints.length - 1; index++)
            {
                // Draw from the first intersection to the next, stop drawing until you see a new intersection line
                if (index % 2 === 0)
                {
                    let start = intersectionPoints[index].absolutePaddedX, // This will contain the start of the x coords to fill
                        end = intersectionPoints[index + 1].absolutePaddedX,    // This will contain the end of the x coords to fill
                        y = intersectionPoints[index].absolutePaddedY;

                    for (var fill = start; fill < end; fill++)
                    {
                        // Remove padding to get absolute coordinates
                        let absoluteCoords = new Point().getAbsoluteCoordinatesFromPadded(pageIndex,renderer,fill,y);

                        if (this.blendMode === "add")
                        {
                            // Necessary check because sometimes the brush draws outside of a page because of brush width
                            if (absoluteCoords.y >= 0 && absoluteCoords.x >= 0 && absoluteCoords.y <= drawingCanvas.height && absoluteCoords.x <= drawingCanvas.width)
                            {
                                // TODO: Can also pass in and fill a matrix
                                let paddedCoords = new Point().getPaddedCoordinatesFromAbsolute(pageIndex, renderer, absoluteCoords.x, absoluteCoords.y),
                                    data = imageCtx.getImageData(paddedCoords.x, paddedCoords.y, 1, 1).data,
                                    colour = new Colour(data[0], data[1], data[2], data[3]);

                                drawingCtx.fillStyle = colour.toHTMLColour();
                                drawingCtx.fillRect(absoluteCoords.x, absoluteCoords.y, 1, 1);
                            }
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