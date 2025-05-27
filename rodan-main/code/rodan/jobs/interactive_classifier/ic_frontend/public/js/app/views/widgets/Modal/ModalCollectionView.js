import Marionette from "marionette";
import ModalView from "views/widgets/Modal/ModalView";

/**
 * A collection of modals.
 */
export default Marionette.CollectionView.extend({
    childView: ModalView
});