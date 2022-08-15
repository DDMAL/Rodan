import $ from 'jquery';
import _ from 'underscore';
import Marionette from 'backbone.marionette';
import ViewInputPortCollection from 'js/Views/Master/Main/InputPort/ViewInputPortCollection';
import ViewInputPortCollectionItem from 'js/Views/Master/Main/InputPort/ViewInputPortCollectionItem';
import ViewInputPortTypeCollection from 'js/Views/Master/Main/InputPortType/ViewInputPortTypeCollection';
import ViewOutputPortCollection from 'js/Views/Master/Main/OutputPort/ViewOutputPortCollection';
import ViewOutputPortTypeCollection from 'js/Views/Master/Main/OutputPortType/ViewOutputPortTypeCollection';

/**
 * View for editing ports.
 */
export default class LayoutViewControlPorts extends Marionette.View
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
        this.addRegions({
            regionControlInputPortTypes: '#region-main_inputporttypes',
            regionControlInputPorts: '#region-main_inputports',
            regionControlOutputPortTypes: '#region-main_outputporttypes',
            regionControlOutputPorts: '#region-main_outputports'
        });
        this._workflowJob = options.workflowjob;
        this._initializeViews(options);
    }

    /**
     * Show the subviews before showing this view.
     */
    onRender()
    {
        this.showChildView('regionControlInputPortTypes', this._inputPortTypeCollectionView);
        this.showChildView('regionControlInputPorts', this._inputPortCollectionView);
        this.showChildView('regionControlOutputPortTypes', this._outputPortTypeCollectionView);
        this.showChildView('regionControlOutputPorts', this._outputPortCollectionView);
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle workflowjob selection.
     */
    _initializeViews(options)
    {
        this._inputPortCollectionView = new ViewInputPortCollection({collection: options.workflowjob.get('input_ports'),
                                                         template: _.template($('#template-main_inputport_collection').text()),
                                                         childView: ViewInputPortCollectionItem,
                                                         childViewOptions: options});
        this._outputPortCollectionView = new ViewOutputPortCollection({collection: options.workflowjob.get('output_ports'),
                                                           childViewOptions: options});
        this._inputPortTypeCollectionView = new ViewInputPortTypeCollection({workflowjob: options.workflowjob,
                                                                 childViewOptions: options});
        this._outputPortTypeCollectionView = new ViewOutputPortTypeCollection({workflowjob: options.workflowjob,
                                                                   childViewOptions: options});
    }
}
LayoutViewControlPorts.prototype.template = _.template($('#template-main_workflowjob_ports').text());
