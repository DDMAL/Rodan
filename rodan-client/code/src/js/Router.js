import Radio from "backbone.radio";
import RODAN_EVENTS from "js/Shared/RODAN_EVENTS";
import ViewResetPassword from "js/Views/Master/Main/User/Individual/ViewResetPassword";
import AppRouter from "marionette.approuter";

const Router = AppRouter.extend({
    controller: {
        resetPassword(uid, token) {
            const options = { uid, token };
            const view = new ViewResetPassword(options);
            Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_HIDE);
            Radio.channel("rodan").request(RODAN_EVENTS.REQUEST__MODAL_SHOW, { title: "Reset Password", content: view });
        }
    },

    appRoutes: {
        "password-reset/:uid/:token": "resetPassword"
    }
});

export default Router;