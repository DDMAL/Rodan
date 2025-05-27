import Configuration from 'js/Configuration';

/**
 * Base class for updaters.
 */
export default class AbstractUpdater
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
	/**
	 * Sets the collections that are to be updated.
	 *
	 * @param {[BaseCollection]} collections collections to be updated.
	 */
	setCollections(collections)
	{
		this.clear();
		this._collections = collections;
	}

	/**
	 * Updates registered collections.
	 */
	update()
	{
		if (this._collections)
		{
			for (var i = 0; i < this._collections.length; i++)
			{
				this._collections[i].syncCollection();
			}
		}
	}
    
    /**
     * Clears registered collections.
     */
    clear()
    {
    	this._collections = null;
    }
}