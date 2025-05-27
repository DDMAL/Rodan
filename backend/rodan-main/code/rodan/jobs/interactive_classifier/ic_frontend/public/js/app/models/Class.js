import Backbone from "backbone";
//import GlyphEvents from "events/GlyphEvents";
//import ClassEvents from "events/ClassEvents";
//import RadioChannels from "radio/RadioChannels";
//import ClassNameUtils from "utils/ClassNameUtils";
//import Glyph from "./Glyph";

/**
 * A Class object within the interactive classifier.
 *
 * @class Class
 */
export default Backbone.Model.extend(
    /**
     * @lends Class.prototype
     */
    {

        defaults:
        {
            name: ""
        }

    });
