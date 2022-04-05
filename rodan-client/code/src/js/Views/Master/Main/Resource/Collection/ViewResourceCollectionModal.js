import $ from 'jquery';
import _ from 'underscore';
import ViewResourceCollection from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollection';
import ViewResourceCollectionModalItem from 'js/Views/Master/Main/Resource/Collection/ViewResourceCollectionModalItem';

/**
 * View for Resource Collection in modal view.
 */
export default class ViewResourceCollectionModal extends ViewResourceCollection {}
ViewResourceCollectionModal.prototype.allowMultipleSelection = true;
ViewResourceCollectionModal.prototype.template = _.template($('#template-modal_resource_collection').text());
ViewResourceCollectionModal.prototype.childView = ViewResourceCollectionModalItem;
