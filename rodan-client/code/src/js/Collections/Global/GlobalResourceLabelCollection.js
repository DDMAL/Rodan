import GlobalCollection from './GlobalCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import ResourceLabel from 'js/Models/ResourceLabel';

let _instance = null;

export default class GlobalResourceLabelCollection extends GlobalCollection
{
    /**
     * Initializes the instance.
     * @throws {Error} thrown
     */
    initialize()
    {
        if (_instance)
        {
            throw new Error('only one instance of this class may exist!');
        }
        _instance = this;
        /** @ignore */
        this.model = ResourceLabel;
        this._route = 'labels';
        this._loadCommand = RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABELS_LOAD;
        this._requestCommand = RODAN_EVENTS.REQUEST__GLOBAL_RESOURCELABEL_COLLECTION;
    }
}
