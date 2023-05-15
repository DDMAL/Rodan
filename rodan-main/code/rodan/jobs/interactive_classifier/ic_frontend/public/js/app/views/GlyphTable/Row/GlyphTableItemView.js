import Marionette from "marionette";
import GlyphEvents from "events/GlyphEvents";
import ClassEvents from "events/ClassEvents";
import GlyphTableItemViewModel from "views/GlyphTable/Row/GlyphTableItemViewModel";
import RadioChannels from "radio/RadioChannels";
import template from "./table-glyph.template.html";
import Geometry from "utils/Geometry";

export default Marionette.ItemView.extend(
    /**
     * @lends GlyphTableItemView.prototype
     */
    {
        template,
        viewModel: undefined,
        tableViewModel: undefined,
        ids: [], // array of ids of selected page glyphs

        tagName: 'div',
        className: "glyph-image-container",

        events: {
            "click .glyph": "onClickGlyph"
        },

        modelEvents: {
            "change": "render"
        },

        /**
         * @class GlyphTableItemView
         *
         * This view is a single Glyph item in the glyph table.  This is the childView
         * for the GlyphTableRowView collection view.
         *
         * This view triggers the events that occur when the user clicks on the glyph.
         *
         * This view also automatically checks if the glyph collides with the
         * selectionBox lasso.
         *
         * Constructor up events for comparing glyph dimensions against selectionBox lasso.
         *
         * @param options
         * @constructs
         */
        initialize: function (options)
        {
            // Call the super constructor
            Marionette.ItemView.prototype.initialize.call(this, options);
            this.viewModel = new GlyphTableItemViewModel();
            this.tableViewModel = options.tableViewModel;

            // Re render when the viewmodel changes activity state
            this.listenTo(this.viewModel, "change:active", this.render);
            var that = this;
            this.listenTo(RadioChannels.edit, GlyphEvents.dragSelect,
                function (boundingBox, additional, isClassifier)
                {
                    var isInClassifierPane = this._parent._parent._parent._parent._parent.collection.is_classifier;
                    var id = this.model.attributes.id;
                    // If drag select is triggered in the classifier glyphs region,
                    // highlight only the classifier glyphs that overlap the bounding box and unhighlight page glyphs.
                    // If drag select instriggered in the page glyphs region,
                    // highlight only the page glyphs that overlap the bounding box and unhighlight classifier glyphs.
                    if (isClassifier)
                    {
                        if (isInClassifierPane)
                        {
                            if (Geometry.rectangleOverlap(that.getPosition(), boundingBox))
                            {
                                RadioChannels.edit.trigger(GlyphEvents.selectGlyph, that.model);
                                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, true);
                            }
                            else if (!additional)
                            {
                                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, false);
                            }
                        }
                        else
                        {
                            RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, false);
                        }
                    }
                    else
                    {
                        if (!isInClassifierPane)
                        {
                            if (Geometry.rectangleOverlap(that.getPosition(), boundingBox))
                            {
                                RadioChannels.edit.trigger(GlyphEvents.selectGlyph, that.model);
                                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, true);
                                if (that.model.get("id_state_manual") && !that.ids.includes(id))
                                {
                                    that.ids.push(id);
                                }

                            }
                            else if (!additional)
                            {
                                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, false);
                            }
                        }
                        else
                        {
                            if (!that.ids.includes(id))
                            {
                                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, id, false);
                            }
                        }
                    }
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.previewSelect,
                function (boundingBox, additional)
                {
                    if (boundingBox)
                    {
                        var pic = document.getElementsByClassName("preview-background")[0];
                        var zoomLevel = pic.getBoundingClientRect().height / pic.dataset.originalHeight;
                        var glyphRect =
                        {
                            left: that.model.get('ulx') * zoomLevel,
                            top: that.model.get('uly') * zoomLevel,
                            right: (that.model.get('ulx') + that.model.get('ncols')) * zoomLevel,
                            bottom: (that.model.get('uly') + that.model.get('nrows')) * zoomLevel
                        }
                        var is_split = this.model.attributes.class_name.startsWith("_split.");
                        var is_train = this.model.attributes.is_training;
                        if (Geometry.rectangleOverlap(glyphRect, boundingBox) && !(is_train) && !(is_split))
                        {
                            // Add this glyph to the collection
                            RadioChannels.edit.trigger(GlyphEvents.selectGlyph, that.model);
                            // jscs:disable
                            RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, that.model.attributes.id, true);
                            // Scroll to the glyph
                            // Checks both manual and unmanual glyphs
                            var elems = Array.from(document.getElementsByClassName("glyph img-thumbnail bg-warning glyph-image"));
                            elems.concat(Array.from(document.getElementsByClassName("glyph img-thumbnail bg-success glyph-image")));

                            for (var i = 0; i < elems.length; i++)
                            {
                                if (elems[i]['href'].split('glyph/')[1].split('/')[0] === that.model.id)
                                {
                                    elems[i].scrollIntoView({inline: "center"});
                                }
                            }
                            // jscs:enable
                        }
                        // If not additional and not a manual classifier glyph
                        // If the glyph is a manual classifier glyph, that means that the the pageGlyph version
                        // of that glyph will control activation and deactivation
                        else if (!additional && (!(that.is_classifier) || this.model.attributes.is_training))
                        {
                            // If it's additional, then we don't deactivate!
                            // false means deactivate
                            // jscs:disable
                            RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, that.model.attributes.id, false);
                            // jscs:enable
                        }
                    }
                }
            );

            this.listenTo(RadioChannels.edit, GlyphEvents.openGlyphEdit, function (model)
            {
                if (that.model.attributes.id !== model.attributes.id)
                {
                    RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, that.model.attributes.id, false);
                }
            });

            this.listenTo(RadioChannels.edit, ClassEvents.openClassEdit, function ()
            {
                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, that.model.attributes.id, false);
            });

            this.listenTo(RadioChannels.edit, GlyphEvents.switchGlyphActivation,
            function (id, toActive)
            {
                if (id === that.model.attributes.id)
                {
                    if (toActive)
                    {
                        that.viewModel.activate();
                    }
                    else
                    {
                        that.viewModel.deactivate();
                    }
                }
            });
        },

        onShow: function()
        {
            var class_table = document.getElementsByClassName("classifier-table-region")[0].getBoundingClientRect();
            this.is_classifier = Geometry.rectangleOverlap(this.getPosition(), class_table);
        },

        /**
         * When the user clicks on a glyph, there are two possible behaviours
         * depending on whether or not the shift key is being held.
         *
         * If the user holds the shift key, then there are two possibilities.
         * If this glyph is already selected, then the glyph is unselected.
         * If the glyph isn't selected, then the glyph is added to the list of
         * currently selected glyphs in the GlyphMultiEditView.
         *
         * If the user is not holding the shift key, then all other glyphs are
         * unselected, the GlyphEditView is opened, and this glyph is selected.
         *
         * @param event jQuery event object.
         */
        onClickGlyph: function (event)
        {
            event.preventDefault();
            if (event.shiftKey)
            {
                // If the glyph is already active, then deactivate it.
                // If the glyph is not already active, then activate it.
                if (this.viewModel.isActive())
                {
                    RadioChannels.edit.trigger(GlyphEvents.deselectGlyph, this.model);
                    RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, this.model.attributes.id, false);
                }
                else
                {
                    RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, this.model.attributes.id, true);
                    RadioChannels.edit.trigger(GlyphEvents.selectGlyph, this.model);
                }
                RadioChannels.edit.trigger(GlyphEvents.openMultiEdit);
            }
            else
            {
                RadioChannels.edit.trigger(GlyphEvents.switchGlyphActivation, this.model.attributes.id, true);
                RadioChannels.edit.trigger(GlyphEvents.deselectAllGlyphs);
                RadioChannels.edit.trigger(GlyphEvents.selectGlyph, this.model);
                RadioChannels.edit.trigger(GlyphEvents.openGlyphEdit, this.model, this.viewModel);
            }
        },

        /**
         * Depending on whether the glyph has been manually identified by the user
         * or automatically identified by Gamera, we apply different CSS styles.
         *
         * @returns {*|string}
         */
        serializeData: function ()
        {
            var data = this.model.toJSON();

            data.outerTag = "";
            if (this.viewModel.isActive())
            {
                data.outerTag = "bg-primary";
            }
            // Figure out which background color will be used
            data.cssTag = "";
            if (this.model.get("id_state_manual") === true)
            {
                data.cssTag = "bg-success";
            }
            else
            {
                data.cssTag = "bg-warning";
            }
            return data;
        },

        /**
         * Get the positional information of the view in the dom.
         *
         * @returns {ClientRect}
         */
        getPosition: function ()
        {
            return this.el.getBoundingClientRect();
        }
    });
