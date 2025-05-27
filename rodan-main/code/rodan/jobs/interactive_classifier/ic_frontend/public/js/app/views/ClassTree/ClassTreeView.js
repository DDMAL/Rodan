import _ from "underscore";
import Marionette from "marionette";
import RadioChannels from "radio/RadioChannels";
import GlyphEvents from "events/GlyphEvents";
import ClassEvents from "events/ClassEvents";
import classNameArrayToRecursiveTree from "./classNameArrayToRecursiveTree";
import ClassTreeViewModel from "views/ClassTree/ClassTreeViewModel"
import RecursiveUnorderedListView from "./RecursiveUnorderedListView";
import RecursiveUnorderedListViewModel from "./RecursiveUnorderedListViewModel";
import template from "./class-tree.template.html";

export default Marionette.LayoutView.extend(
    /**
     * @lends ClassTreeView.prototype
     */
    {
        template,

        regions: {
            "classTreeRegion": ".class-tree"
        },

        modelEvents: {
            "change": "showSubTree"
        },

        /**
         * @class ClassTreeView
         *
         * This view is the list of class names in the top-left corner of the Interactive Classifier GUI.  This view should
         * update itself whenever a new class name is created.
         *
         * @constructs
         */
        initialize: function ()
        {
            // Set up the event listener to handle re-rendering the view whenever
            // a new Glyph class name is created.
            var that = this;
            this.listenTo(RadioChannels.edit, GlyphEvents.setGlyphName, function (newClassName)
            {
                // Add the model to the class_names
                var oldClassNameList = that.model.get("class_names");

                //Don't display the new class if it's a part of a group or a split
                if (!newClassName.startsWith("_group._part") && !newClassName.startsWith("_split"))
                {
                    var newClassNameList = _.union(oldClassNameList, [newClassName]);

                    if (newClassNameList.length !== oldClassNameList.length)
                    {
                        // Set the new list
                        that.model = new ClassTreeViewModel({
                            class_names: newClassNameList.sort()
                        });
                        // Re-render the view
                        that.showSubTree();
                    }
                    else
                    {
                        that.showSubTree();
                    }
                }
            }),
            this.listenTo(RadioChannels.edit, ClassEvents.deleteClass, function (deletedClassName)
            {
                // Add the model to the class_names
                var classNameList = that.model.get("class_names");
                var filteredList = classNameList.filter(name => name !== deletedClassName &&
                  !name.startsWith(deletedClassName + "."));
                // Set the new list
                that.model = new ClassTreeViewModel({
                    class_names: filteredList.sort()
                });
                // Re-render the view
                that.showSubTree();
            }),
            this.listenTo(RadioChannels.edit, ClassEvents.renameClass, function (oldClassName, newClassName)
            {
                var classNameList = that.model.get("class_names");
                for (var i = 0; i < classNameList.length; i++)
                {
                    if (classNameList[i].startsWith(oldClassName + ".") || classNameList[i] === oldClassName)
                    {
                        classNameList[i] = classNameList[i].replace(oldClassName, newClassName);
                    }
                }
                // remove duplicates from the list
                var uniqueList = classNameList.filter(function(item, pos)
                {
                    return classNameList.indexOf(item) === pos;
                });
                // Set the new list
                that.model = new ClassTreeViewModel({
                    class_names: uniqueList.sort()
                });
                // Re-render the view
                that.showSubTree();
            });
        },

        onShow: function ()
        {
            this.showSubTree();
        },

        /**
         * Show the tree of class names.
         */
        showSubTree: function ()
        {
            var classNames = this.model.get("class_names");
            var mod = new RecursiveUnorderedListViewModel({
                value: undefined,
                children: []
            });
            classNameArrayToRecursiveTree(classNames, mod);
            this.classTreeRegion.show(new RecursiveUnorderedListView({model: mod}));
        }
    }
);
