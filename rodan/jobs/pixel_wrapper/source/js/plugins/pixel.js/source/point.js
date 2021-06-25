/*jshint esversion: 6 */
export class Point
{
    /**
     * The relative origins allow to position the point at the same page location no matter what the zoom level is
     * @param relativeOriginX
     * @param relativeOriginY
     * @param pageIndex
     */
    constructor (relativeOriginX, relativeOriginY, pageIndex)
    {
        this.relativeOriginX = relativeOriginX;
        this.relativeOriginY = relativeOriginY;
        this.pageIndex = pageIndex;
    }

    /**
     * Calculates the coordinates of a point on a page in pixels given the zoom level
     * where the top left corner of the page always represents the (0,0) coordinate.
     * The function scales the relative coordinates to the required zoom level.
     * @param zoomLevel
     * @returns {{x: number, y: number}}
     */
    getCoordsInPage (zoomLevel)
    {
        let scaleRatio = Math.pow(2,zoomLevel);
        return {
            x: this.relativeOriginX * scaleRatio,
            y: this.relativeOriginY * scaleRatio
        };
    }

    /**
     * Calculates the coordinates of a point on the diva canvas (viewport) in pixels, where the top left corner of the canvas
     * represents the (0,0) coordinate.
     * This is relative to the viewport padding.
     * @param zoomLevel
     * @param pageIndex
     * @param renderer
     * @returns {{x: number, y: number}}
     */
    getCoordsInViewport (zoomLevel, pageIndex, renderer)
    {
        const viewportPaddingX = Math.max(0, (renderer._viewport.width - renderer.layout.dimensions.width) / 2);
        const viewportPaddingY = Math.max(0, (renderer._viewport.height - renderer.layout.dimensions.height) / 2);

        let absoluteCoordinates = this.getCoordsInPage(zoomLevel);

        // Calculates where the highlights should be drawn as a function of the whole canvas coordinates system
        // (to make it look like it is on top of a page in Diva)
        let offsetX = renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX + absoluteCoordinates.x,
            offsetY = renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY + absoluteCoordinates.y;

        return {
            x: offsetX,
            y: offsetY
        };
    }

    /**
     * Calculates the coordinates of a point on a page in pixels
     * from the padded coordinates used to display the point on diva canvas (viewport)
     * @param pageIndex
     * @param renderer
     * @param paddedX
     * @param paddedY
     * @returns {{x: number, y: number}}
     */
    getAbsoluteCoordinatesFromPadded (pageIndex, renderer, paddedX, paddedY)
    {
        const viewportPaddingX = Math.max(0, (renderer._viewport.width - renderer.layout.dimensions.width) / 2);
        const viewportPaddingY = Math.max(0, (renderer._viewport.height - renderer.layout.dimensions.height) / 2);

        return {
            x: Math.round(paddedX - (renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX)),
            y: Math.round(paddedY - (renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY))
        };
    }

    /**
     * Calculates the coordinates of a point on diva canvas (viewport) in pixels
     * from the absolute coordinates on the page
     * @param pageIndex
     * @param renderer
     * @param absoluteX
     * @param absoluteY
     * @returns {{x: *, y: *}}
     */
    getPaddedCoordinatesFromAbsolute (pageIndex, renderer, absoluteX, absoluteY)
    {
        const viewportPaddingX = Math.max(0, (renderer._viewport.width - renderer.layout.dimensions.width) / 2);
        const viewportPaddingY = Math.max(0, (renderer._viewport.height - renderer.layout.dimensions.height) / 2);

        // Calculates where the highlights should be drawn as a function of the whole canvas coordinates system
        // (to make it look like it is on top of a page in Diva)
        return {
            x: renderer._getImageOffset(pageIndex).left - renderer._viewport.left + viewportPaddingX + absoluteX,
            y: renderer._getImageOffset(pageIndex).top - renderer._viewport.top + viewportPaddingY + absoluteY
        };
    }

    /**
     * Calculates the coordinates of a point relative to a page (used to calculate the absolute coordinates at different zoom levels) in pixels
     * from the padded coordinates used to display the point on diva canvas (viewport)
     * @param pageIndex
     * @param renderer
     * @param paddedX
     * @param paddedY
     * @param zoomLevel
     * @returns {{x: number, y: number}}
     */
    getRelativeCoordinatesFromPadded (pageIndex, renderer, paddedX, paddedY, zoomLevel)
    {
        let scaleRatio = Math.pow(2, zoomLevel);

        const viewportPaddingX = Math.max(0, (renderer._viewport.width - renderer.layout.dimensions.width) / 2);
        const viewportPaddingY = Math.max(0, (renderer._viewport.height - renderer.layout.dimensions.height) / 2);

        // Calculates where the highlights should be drawn as a function of the whole webpage coordinates
        // (to make it look like it is on top of a page in Diva)
        let absoluteRectOriginX = paddedX - renderer._getImageOffset(pageIndex).left + renderer._viewport.left -  viewportPaddingX,
            absoluteRectOriginY = paddedY - renderer._getImageOffset(pageIndex).top + renderer._viewport.top - viewportPaddingY;

        return{
            x: absoluteRectOriginX/scaleRatio,
            y: absoluteRectOriginY/scaleRatio
        };
    }
}