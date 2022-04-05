import $ from 'jquery';
import _ from 'underscore';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';
import ViewOutputPortTypeCollectionItem from './ViewOutputPortTypeCollectionItem';

/**
 * OutputPortTYpe Collection view.
 */
export default class ViewOutputPortTypeCollection extends Marionette.CollectionView
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
        this.collection = job.get('output_port_types');
    }
}
ViewOutputPortTypeCollection.prototype.modelEvents = {
    'all': 'render'
};
ViewOutputPortTypeCollection.prototype.template = _.template($('#template-main_outputporttype_collection').text());
ViewOutputPortTypeCollection.prototype.childView = ViewOutputPortTypeCollectionItem;
ViewOutputPortTypeCollection.prototype.childViewContainer = 'tbody';
