import Marionette from 'backbone.marionette';

/**
 * Base View for Collections.
 */
export default class BaseViewCollection extends Marionette.CollectionView {}
BaseViewCollection.prototype.modelEvents = { 'all': 'render' };
BaseViewCollection.prototype.childViewContainer = 'tbody';
BaseViewCollection.prototype.allowMultipleSelection = false;
BaseViewCollection.prototype.el = '<div class="content-wrapper column-content single-project-view-collection-wrapper"></div>';