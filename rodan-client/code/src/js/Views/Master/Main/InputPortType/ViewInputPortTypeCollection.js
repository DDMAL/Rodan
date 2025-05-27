import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';
import ViewInputPortTypeCollectionItem from './ViewInputPortTypeCollectionItem';

/**
 * InputPortType Collection view.
 */
export default class ViewInputPortTypeCollection extends Marionette.CollectionView
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     *
     * @param {object} options Marionette.View options object; 'options.workflowjob' (WorkflowJob) must also be provided
     */
    initialize(options)
    {
        var jobCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_JOB_COLLECTION);
        var job = jobCollection.get(options.workflowjob.getJobUuid());
        /** @ignore */
        this.collection = job.get('input_port_types');
    }
}
ViewInputPortTypeCollection.prototype.modelEvents = {
    'all': 'render'
};
ViewInputPortTypeCollection.prototype.template = _.template($('#template-main_inputporttype_collection').text());
ViewInputPortTypeCollection.prototype.childView = ViewInputPortTypeCollectionItem;
ViewInputPortTypeCollection.prototype.childViewContainer = 'tbody';
