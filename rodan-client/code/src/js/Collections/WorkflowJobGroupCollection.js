import BaseCollection from './BaseCollection';
import WorkflowJobGroup from 'js/Models/WorkflowJobGroup';

/**
 * Collection of WorkflowJobGroup models.
 */
export default class WorkflowJobGroupCollection extends BaseCollection
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     * @todo doing a fetch on a collection isn't firing events, so I need to do this. See https://github.com/DDMAL/rodan-client/issues/77
     */
    initialize()
    {
        /** @ignore */
        this.model = WorkflowJobGroup;
        this._route = 'workflowjobgroups';
        this.on('sync', (collection, response, options) => this._onSync(collection, response, options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
	/**
	 * Every sync, just save each model.
	 */
	_onSync(collection, response, options)
	{
		for (var i = 0; i < collection.length; i++)
		{
			var model = collection.at(i);
			model.save({}, {patch: true});
		}
	}
}
