/*jshint esversion: 6 */
import {Shape} from './shape';
import {Circle} from './circle';
import {Point} from './point';

export class Line extends Shape
{
    constructor (startPoint, endPoint, lineWidth, lineJoin, blendMode)
    {
        super(startPoint, blendMode);
        this.endPoint = endPoint;
        this.lineWidth = lineWidth;
        this.lineJoin = lineJoin;
    }

    getLineEquation ()
    {
        //TODO: Implement function
    }

    /**
     * Calculates the angle of the line.
     * The angle of a horizontal line is 0 degrees, angles increase in the clockwise direction
     * @param zoomLevel
     * @param pageIndex
     * @param renderer
     * @returns {number}
     */
    getAngleRad (zoomLevel, pageIndex, renderer)
    {
        let startPointAbsolutePaddedCoords = this.origin.getCoordsInViewport(zoomLevel, pageIndex, renderer),
            endPointAbsolutePaddedCoords = this.endPoint.getCoordsInViewport(zoomLevel, pageIndex, renderer);

        return Math.atan2(endPointAbsolutePaddedCoords.y - startPointAbsolutePaddedCoords.y,
            endPointAbsolutePaddedCoords.x - startPointAbsolutePaddedCoords.x);
    }

    /**
     * draws a line of a certain layer in a canvas using viewport coordinates (padded coordinates)
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

        let startPointAbsoluteCoordsWithPadding = this.origin.getCoordsInViewport(zoomLevel, pageIndex, renderer),
            endPointAbsoluteCoordsWithPadding = this.endPoint.getCoordsInViewport(zoomLevel, pageIndex, renderer);

        ctx.beginPath();
        ctx.strokeStyle = layer.colour.toHTMLColour();
        ctx.lineWidth = this.lineWidth * scaleRatio;
        ctx.lineJoin = this.lineJoin;
        ctx.moveTo(startPointAbsoluteCoordsWithPadding.x, startPointAbsoluteCoordsWithPadding.y);
        ctx.lineTo(endPointAbsoluteCoordsWithPadding.x, endPointAbsoluteCoordsWithPadding.y);
        ctx.closePath();
        ctx.stroke();
    }

    /**
     * draws a line of a certain layer in a canvas using absolute page coordinates
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

        let startPointAbsoluteCoords = this.origin.getCoordsInPage(zoomLevel),
            endPointAbsoluteCoords = this.endPoint.getCoordsInPage(zoomLevel);

        ctx.beginPath();
        ctx.strokeStyle = layer.colour.toHTMLColour();
        ctx.lineWidth = this.lineWidth * scaleRatio;
        ctx.lineJoin = this.lineJoin;
        ctx.moveTo(startPointAbsoluteCoords.x, startPointAbsoluteCoords.y);
        ctx.lineTo(endPointAbsoluteCoords.x, endPointAbsoluteCoords.y);
        ctx.closePath();
        ctx.stroke();
    }

    /**
     * Gets all the pixels spanned by a line with round edges. Draws the image data that the line covers (from the imageCanvas) in the drawingCanvas
     * @param layer
     * @param pageIndex
     * @param zoomLevel
     * @param renderer
     * @param drawingCanvas
     * @param imageCanvas
     */
    getPixels (layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas)
    {
        let point1 = this.origin.getCoordsInViewport(zoomLevel, pageIndex, renderer),
            point2 = this.endPoint.getCoordsInViewport(zoomLevel, pageIndex, renderer),
            scaleRatio = Math.pow(2,zoomLevel),
            absoluteLineWidth = this.lineWidth * scaleRatio,
            highlightPageIndex = this.origin.pageIndex;

        if (pageIndex !== highlightPageIndex)
            return;

        // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
        // (to make it look like it is on top of a page in Diva)
        new Circle(this.origin, this.lineWidth/2, this.blendMode).getPixels(layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas);
        new Circle(this.endPoint, this.lineWidth/2, this.blendMode).getPixels(layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas);

        let ang = this.getAngleRad(zoomLevel,pageIndex,renderer);

        // find the first point on the circumference that is orthogonal
        // to the line intersecting the two circle origins
        // ie tangent 1
        // These are values with padding
        var start1 = {
            absolutePaddedX: point1.x + Math.cos(ang + Math.PI / 2) * absoluteLineWidth / 2,
            absolutePaddedY: point1.y + Math.sin(ang + Math.PI / 2) * absoluteLineWidth / 2
        };
        var end1 = {
            absolutePaddedX: point2.x + Math.cos(ang + Math.PI / 2) * absoluteLineWidth / 2,
            absolutePaddedY: point2.y + Math.sin(ang + Math.PI / 2) * absoluteLineWidth / 2
        };

        // find the second point on the circumference that is orthogonal
        // to the line intersecting the two circle origins
        // ie tangent 2
        var start2 = {
            absolutePaddedX: point1.x + Math.cos(ang - Math.PI / 2) * absoluteLineWidth / 2,
            absolutePaddedY: point1.y + Math.sin(ang - Math.PI / 2) * absoluteLineWidth / 2
        };
        var end2 = {
            absolutePaddedX: point2.x + Math.cos(ang - Math.PI / 2) * absoluteLineWidth / 2,
            absolutePaddedY: point2.y + Math.sin(ang - Math.PI / 2) * absoluteLineWidth / 2
        };

        // get ymax and ymin
        let ymax = Math.round(Math.max(start1.absolutePaddedY, start2.absolutePaddedY, end1.absolutePaddedY, end2.absolutePaddedY)),
            ymin = Math.round(Math.min(start1.absolutePaddedY, start2.absolutePaddedY, end1.absolutePaddedY, end2.absolutePaddedY)),
            pairOfEdges = [[start1, end1], [start2, end2], [start1, start2], [end1, end2]];

        // Logic for polygon fill using scan lines
        new Shape(new Point(0,0,0), this.blendMode).getPixels(layer, pageIndex, zoomLevel, renderer, drawingCanvas, imageCanvas, ymax, ymin, pairOfEdges);
    }
}