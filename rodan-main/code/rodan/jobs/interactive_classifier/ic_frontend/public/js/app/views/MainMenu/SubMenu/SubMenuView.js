import Marionette from "marionette";
import SubMenuLinkView from "views/MainMenu/SubMenu/SubMenuLinkView";

export default Marionette.CollectionView.extend({
    childView: SubMenuLinkView,

    tagName: 'ul'
});