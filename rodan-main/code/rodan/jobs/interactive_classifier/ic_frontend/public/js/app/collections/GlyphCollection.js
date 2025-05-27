import Backbone from "backbone";
import Glyph from "models/Glyph";

/**
 * A collection of Glyph models.
 *
 * @class GlyphCollection
 */
export default Backbone.Collection.extend(
    /**
     * @lends GlyphCollection.prototype
     */
    {
        model: Glyph,

        /**
         * In general, we sort Glyphs by reverse confidence.  So, in the glyph table, each row shows the glyphs with
         * highest confidence first.
         *
         * @param glyph
         * @returns {number}
         */
        comparator: function (glyph)
        {
            return -glyph.get("confidence");
        }
    });