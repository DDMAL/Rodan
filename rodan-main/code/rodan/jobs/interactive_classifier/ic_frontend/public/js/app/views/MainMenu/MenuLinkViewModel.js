import Backbone from "backbone";

export default Backbone.Model.extend({
    defaults: {
        url: "#",
        text: "Link",
        clickEvent: null,
        subLinks: undefined,
        icon: null
    }
});
