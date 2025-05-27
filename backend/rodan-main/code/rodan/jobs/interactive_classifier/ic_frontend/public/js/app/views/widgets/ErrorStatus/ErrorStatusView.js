import Marionette from "marionette";
import StatusEnum from "views/widgets/ErrorStatus/StatusEnum";
import template from "./error-status.template.html";

/**
 * A view which displays some error status to the user.
 */
export default Marionette.ItemView.extend({
    template,

    modelEvents: {
        //"change:status": "statusChanged",
        "change:text": "textChanged"
    },

    textChanged: function ()
    {
        this.render();
    },

    serializeData: function ()
    {
        var tag = "";

        if (this.model.get("status") === StatusEnum.success)
        {
            tag = ' class="alert alert-success" role="alert"';
        }
        else if (this.model.get("status") === StatusEnum.error)
        {
            tag = ' class="alert alert-warning" role="alert"'
        }

        return {
            tag: tag,
            text: this.model.get("text")
        }
    }
});
