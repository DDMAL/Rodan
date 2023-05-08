/**
 * Provide general, global configuration for Backbone and Marionette.
 */

import _ from "underscore";
import App from "App";
import Backbone from "backbone";
import Marionette from "marionette";

// Marionette inspector
if (window.__agent)
{
    window.__agent.start(Backbone, Marionette);
}

/**
 * Throw an error if something tries to load a template by ID.
 *
 * This monkey patching is the recommended way of customizing Marionette
 * template loading.
 *
 * @param {string} templateId
 */
Marionette.TemplateCache.prototype.loadTemplate = function (templateId)
{
    throw new Error(`Cannot load template "${templateId}" by ID. Load it via import instead.`);
};

Marionette.Behaviors.behaviorsLookup = _.constant(App.behaviors);

