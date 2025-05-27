import Marionette from "marionette";
import GlyphTableItemView from "views/GlyphTable/Row/GlyphTableItemView";
import template from "./table-row.template.html";

export default Marionette.LayoutView.extend({
    template,
    tagName: "tr",
    tableViewModel: undefined,

    /**
     * @class GlyphTableRowView
     *
     * This view is a row in the GlyphTableView.
     *
     * @param options
     * @constructs GlyphTableRowView
     */
    initialize: function (options)
    {
        // Call the super constructor
        Marionette.ItemView.prototype.initialize.call(this, options);

        this.tableViewModel = options.tableViewModel;
    },

    regions: {
        "elementsRegion": ".elements",
        "classifiedElementsRegion": ".classified-elements"
    },

    onShow: function ()
    {
        var view = new Marionette.CollectionView({
            childView: GlyphTableItemView,
            collection: this.model.get("glyphs"),
            reorderOnSort: true
            // sort: false
        });
        view.childViewOptions = function ()
        {
            return {
                tableViewModel: this.tableViewModel
            }
        };
        this.elementsRegion.show(view);
    }
})
