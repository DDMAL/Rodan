import Backbone from "backbone";
import Marionette from "marionette";
import MenuLinkView from "views/MainMenu/MenuLinkView";
import MenuLinkViewModel from "views/MainMenu/MenuLinkViewModel";
import MenuViewModel from "views/MainMenu/MenuViewModel";
import MainMenuEvents from "events/MainMenuEvents";
import Strings from "localization/Strings";
import template from "./main-menu.template.html";
import RadioChannels from "radio/RadioChannels";

/**
 * The main menu which renders at the top of the window.
 */
export default Marionette.CompositeView.extend({
    template,
    childView: MenuLinkView,
    childViewContainer: ".navbar-left",

    events: {
        "click .re-classify": "reClassify",
        "click .group": "group",
        "click .finalize": "finalize"
    },

    initialize: function ()
    {
        // A model to handle the main properties of the menu
        this.model = new MenuViewModel({
            title: Strings.siteTitle,
            reClassify: Strings.menuSubmitLabel,
            group: Strings.menuGroupLabel,
            finalize: Strings.menuFinalizeLabel
        });
        // A collection representing the menu links
        var menuLinks = new Backbone.Collection();
        menuLinks.add(new MenuLinkViewModel({
            url: "#",
            text: Strings.saveChanges,
            clickEvent: MainMenuEvents.clickSaveChanges,
            icon: "glyphicon-floppy-disk"
        }));
        menuLinks.add(new MenuLinkViewModel({
            url: "#",
            text: Strings.undoAll,
            clickEvent: MainMenuEvents.clickUndoAll,
            icon: "glyphicon-repeat"
        }));
        this.collection = menuLinks;
    },

    reClassify: function ()
    {
        RadioChannels.menu.trigger(MainMenuEvents.clickSubmitCorrections);
    },
    group: function ()
    {
        RadioChannels.menu.trigger(MainMenuEvents.clickGroupClassify);
    },
    finalize: function ()
    {
        RadioChannels.menu.trigger(MainMenuEvents.clickFinalizeCorrections);
    }
});
