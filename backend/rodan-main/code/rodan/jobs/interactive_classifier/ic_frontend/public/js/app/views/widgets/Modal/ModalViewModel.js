import Backbone from "backbone";

/**
 * @class ModalViewModel
 *
 * This ViewModel controls the state of a modal.
 *
 * The innerView property points to an arbitrary view that is rendered
 * in the body of the modal.
 *
 * The isClosable property determines whether or not the user has the power to manually close the view.
 */
export default Backbone.Model.extend(
    /**
     * @lends ModalViewModel.prototype
     */
    {
        defaults: {
            title: "",
            innerView: undefined,
            isCloseable: false,
            isHiddenObject: true
        },

        /**
         * Open the modal.
         */
        open: function ()
        {
            this.trigger("open");
        },

        /**
         * Close the modal.
         */
        close: function ()
        {
            this.trigger("close");
        }
    });
