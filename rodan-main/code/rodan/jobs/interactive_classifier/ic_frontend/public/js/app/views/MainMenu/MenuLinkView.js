import Marionette from "marionette";
import Radio from "backbone.radio";
import SubMenuView from "views/MainMenu/SubMenu/SubMenuView";
import template from "./main-menu-link.template.html";

export default Marionette.LayoutView.extend({
    template,

    tagName: 'li',
    className: "dropdown",

    events: {
        "click .menu-link": "onClick"
    },

    regions: {
        dropDownRegion: ".dropdown-menu"
    },

    onClick: function (event)
    {
        event.preventDefault();
        Radio.trigger("menu", this.model.get("clickEvent"));
    },

    onShow: function ()
    {
        if (this.model.get("subLinks"))
        {
            this.dropDownRegion.show(new SubMenuView({
                collection: this.model.get("subLinks")
            }));
        }
    }
});
