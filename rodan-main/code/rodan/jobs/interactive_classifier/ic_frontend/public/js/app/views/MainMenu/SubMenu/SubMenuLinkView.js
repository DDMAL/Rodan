import Marionette from "marionette";
import Radio from "backbone.radio";
import template from "./main-menu-sub-link.template.html";

export default Marionette.ItemView.extend({
    template,

    tagName: "li",

    events: {
        "click a": "onClick"
    },

    onClick: function ()
    {
        console.log("click: ", this.model.get("clickEvent"));
        Radio.trigger("menu", this.model.get("clickEvent"));
    }
});
