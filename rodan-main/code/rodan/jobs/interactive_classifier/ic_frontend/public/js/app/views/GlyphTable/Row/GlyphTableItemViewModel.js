import Backbone from "backbone";

/**
 * @class GlyphTableItemViewModel
 */
export default Backbone.Model.extend(
    /**
     * @lends GlyphTableItemViewModel.prototype
     */
    {
        defaults: {
            active: false
        },

        isActive: function ()
        {
            return this.get("active") === true;
        },

        activate: function ()
        {
            this.set("active", true);
        },

        deactivate: function ()
        {
            this.set("active", false);
        }
    }
);
