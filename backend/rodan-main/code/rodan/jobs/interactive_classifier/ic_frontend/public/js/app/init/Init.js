import "init/BackboneCustomization";
import "jquery";
import "underscore";
import "marionette";
import "bootstrap";
import "modernizr";
import Backbone from "backbone";
import App from "App";

App.on('start', function ()
{
    // We don't support hash URL fallbacks at the moment because we're not loading the routing code
    // in the root URL page, so hash links are never forwarded. There might also be infinite loops in
    // the manuscript detail view (not really sure; this would need more looking into).

    // According to caniuse, 88% of browsers support pushState (http://caniuse.com/#feat=history), with
    // IE 9 being the only support case we really need to worry about. For now, do hard reloads on page
    // changes and hope caching will be our salvation.

    Backbone.history.start({pushState: true, hashChange: false});
});

App.start();
