/*jshint esversion: 6 */
export class Path
{
    constructor (brushSize, blendMode)
    {
        this.points = [];
        this.brushSize = brushSize;
        this.type = "path";
        this.blendMode = blendMode;
        this.lastAbsX = 0;
        this.lastAbsY = 0;
    }

    addPointToPath (point)
    {
        this.points.push(point);
    }

    drawInViewport (layer, pageIndex, zoomLevel, renderer, canvas)
    {
        let isDown = false;
        this.points.forEach((point) => {
            this.connectPoint(layer, point, pageIndex, zoomLevel, isDown, renderer, canvas, "viewport");
            isDown = true;
        });
    }

    drawOnPage (layer, pageIndex, zoomLevel, renderer, canvas)
    {
        let isDown = false;
        this.points.forEach((point) => {
            this.connectPoint(layer, point, pageIndex, zoomLevel, isDown, renderer, canvas, "page");
            isDown = true;
        });
    }

    /**
     * Calculates the coordinates of the point to be added depending on the specified coordinates system
     * Places a point in the path
     * Only connects a point to the previous on if isDown is true
     * This is mainly used when the user is in the process of drawing the path
     * @param layer
     * @param point
     * @param pageIndex
     * @param zoomLevel
     * @param isDown
     * @param renderer
     * @param canvas
     * @param coordinatesSystem
     */
    connectPoint (layer, point, pageIndex, zoomLevel, isDown, renderer, canvas, coordinatesSystem)
    {
        let scaleRatio = Math.pow(2, zoomLevel),
            ctx = canvas.getContext('2d');

        if (pageIndex !== point.pageIndex)
            return;

        // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
        // (to make it look like it is on top of a page in Diva)
        let coordinates;
        switch (coordinatesSystem)
        {
            case "viewport":
                coordinates = point.getCoordsInViewport(zoomLevel, pageIndex, renderer);
                break;
            case "page":
                coordinates = point.getCoordsInPage(zoomLevel);
                break;
            default:
                coordinates = point.getCoordsInViewport(zoomLevel, pageIndex, renderer);
        }

        let highlightXOffset = coordinates.x,
            highlightYOffset = coordinates.y;

        if (isDown)
        {
            if (this.blendMode === "add")
            {
                ctx.globalCompositeOperation="source-over";
                ctx.beginPath();
                ctx.strokeStyle = layer.colour.toHTMLColour();
                ctx.lineWidth = this.brushSize * scaleRatio;
                ctx.lineJoin = "round";
                ctx.moveTo(this.lastAbsX, this.lastAbsY);
                ctx.lineTo(highlightXOffset, highlightYOffset);
                ctx.closePath();
                ctx.stroke();
            }

            else if (this.blendMode === "subtract")
            {
                ctx.globalCompositeOperation="destination-out";
                ctx.beginPath();
                ctx.strokeStyle = "rgba(250,250,250,1)"; // It is important to have the alpha always equal to 1. RGB are not important when erasing
                ctx.lineWidth = this.brushSize * scaleRatio;
                ctx.lineJoin = "round";
                ctx.moveTo(this.lastAbsX, this.lastAbsY);
                ctx.lineTo(highlightXOffset, highlightYOffset);
                ctx.closePath();
                ctx.stroke();
            }
            ctx.globalCompositeOperation="source-over";
        }
        this.lastAbsX = highlightXOffset;
        this.lastAbsY = highlightYOffset;
    }
}