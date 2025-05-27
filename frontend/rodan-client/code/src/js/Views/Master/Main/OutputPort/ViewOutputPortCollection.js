import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import ViewOutputPortCollectionItem from './ViewOutputPortCollectionItem';

/**
 * OutputPort Collection view.
 */
export default class ViewOutputPortCollection extends BaseViewCollection {}
ViewOutputPortCollection.prototype.template = _.template($('#template-main_outputport_collection').text());
ViewOutputPortCollection.prototype.childView = ViewOutputPortCollectionItem;
