import Marionette from "marionette";

/**
 * @class RootView
 *
 * This view is the "root" HTML element of the entire application.  App.js manages this view.  This view doesn't have
 * any functionality beyond the container, navigation, and modal regions.
 *
 * RodanDashboardView is shown in the container region.
 *
 * MainMenuView is shown in the navigation region.
 *
 * A bunch of modals are shown in the modal region.
 *
 * @constructs RootView
 */
export default Marionette.LayoutView.extend({
    el: 'body',

    regions: {
        container: "#content",
        navigation: "#navigation",
        modal: "#root-modal"
    }
});