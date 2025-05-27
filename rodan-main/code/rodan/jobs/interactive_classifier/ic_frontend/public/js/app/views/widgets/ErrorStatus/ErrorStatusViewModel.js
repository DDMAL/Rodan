import Backbone from "backbone";
import StatusEnum from "views/widgets/ErrorStatus/StatusEnum";

export default Backbone.Model.extend({

    defaults: {
        status: StatusEnum.none,
        text: ""
    },

    error: function (message)
    {
        this.set("status", StatusEnum.error);
        this.set("text", String(message));
    },

    success: function (message)
    {
        this.set("status", StatusEnum.success);
        this.set("text", String(message));
    }
});
