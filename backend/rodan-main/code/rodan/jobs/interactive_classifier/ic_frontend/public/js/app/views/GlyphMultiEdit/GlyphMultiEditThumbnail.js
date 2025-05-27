import Marionette from "marionette";
import template from "views/GlyphMultiEdit/thumbnail.template.html";

export default Marionette.ItemView.extend({
    template,
    tagName: "tr",

    modelEvents: {
        "change": "render"
    },

    serializeData: function ()
    {
        return this.model.toJSON();
    }
});