import $ from 'jquery';
import _ from 'underscore';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';

/**
 * View for InputPort Collection.
 */
export default class ViewInputPortCollection extends BaseViewCollection {}
ViewInputPortCollection.prototype.template = _.template($('#template-main_inputport_collection').text());
