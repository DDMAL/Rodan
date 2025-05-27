/**
 * Functions for doing geometry.
 *
 * @module Geometry
 */
export default {

    /**
     * A box with dimensions.
     *
     * @typedef {{left: number, right: number, top: number, bottom: number}} BoundingBox
     */

    /**
     * Test if two rectangles overlap.
     *
     * @param {BoundingBox} rectangleA - The first rectangle.
     * @param {BoundingBox} rectangleB - The second rectangle.
     * @returns {boolean} True if the rectangles intersect.
     */
    rectangleOverlap: function (rectangleA, rectangleB)
    {
        return rectangleA.left < rectangleB.right && rectangleA.right > rectangleB.left &&
            rectangleA.top < rectangleB.bottom && rectangleA.bottom > rectangleB.top;
    }
}