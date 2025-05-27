import Backbone from "backbone";
import _ from "underscore";

/**
 * @class RecursiveUnorderedListViewModel
 *
 * ViewModel for RecursiveUnorderedListView.  This model is the node of a tree.
 */
var RecursiveUnorderedListViewModel = Backbone.Model.extend(
    /**
     * @lends RecursiveUnorderedListViewModel.prototype
     */
    {
        defaults: {
            value: undefined,
            children: []
        },

        /**
         * If a value is already a child, then get its node.  Otherwise, append a
         * new node and get that.
         *
         * @param value
         * @returns {RecursiveUnorderedListViewModel} - The node with the value.
         */
        getOrAppendChild: function (value)
        {
            var children = this.get("children");

            var matchingChild = _.find(
                children,
                (child) => child.get("value") === value
            );
            if (matchingChild)
            {
                return matchingChild;
            }
            else
            {
                // Append a child
                var newChild = new RecursiveUnorderedListViewModel({
                    value: value,
                    children: []
                });
                this.get("children").push(newChild);
                return newChild;
            }
        },

        deleteChild: function (value)
        {
            var children = this.get("children");
            var matchingChild = _.find(
                children,
                (child) => child.get("value") === value
            );
            if (matchingChild)
            {
                var index = children.indexOf(matchingChild);
                this.get("children").splice(index,1);
            }
        }

    });

export default RecursiveUnorderedListViewModel;