import Backbone from "backbone";

export default Backbone.Model.extend({
    defaults: {
        src: "#",
        class: undefined,
        style: undefined,
        width: undefined,
        height: undefined
    }
})