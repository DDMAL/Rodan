import $ from 'jquery';
import _ from 'underscore';
import tagsInput from 'tags-input';
import BehaviorTable from 'js/Behaviors/BehaviorTable';
import BaseViewCollection from 'js/Views/Master/Main/BaseViewCollection';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Radio from 'backbone.radio';

/**
 * View for Resource Collection.
 */
export default class ViewResourceCollection extends BaseViewCollection
{
    initialize(options) {
        this.allowMultipleSelection = true;
        this.octetStreamType = '';
        this.inputInitialized = false;
    }
	/**
	 * Handle file button.
	 */
    _handleClickButtonFile()
    {
        for (var i = 0; i < this.ui.fileInput[0].files.length; i++)
        {
        	var file = this.ui.fileInput[0].files[i];
          var escapedFile = new File([file.slice(0, file.size)], _.escape(_.escape(file.name)));  // This won't work with only one escape!
    	    Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__RESOURCE_CREATE,
              {
                  project: this.model,
                  file: escapedFile,
                  resourcetype: this.octetStreamType,
                  label_names: this.ui.labelInput[0].value
              }
          );
    	}
	    this.ui.fileInput.replaceWith(this.ui.fileInput = this.ui.fileInput.clone(true));
    }

    /**
     * On render populate the ResourceTypeList dropdown.
     */
    onRender()
    {
        this.inputInitialized = false;
        var resourceTypeCollection = Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__GLOBAL_RESOURCETYPE_COLLECTION);
        for (var i = 0; i < resourceTypeCollection.length; i++)
        {
        	var resourceType = resourceTypeCollection.at(i);
            if (resourceType.attributes.mimetype === 'application/octet-stream') {
                this.octetStreamType = resourceType.attributes.url;
                break;
            }
        }
    }

    onAttach()
    {
        if (!this.inputInitalized && document.getElementById('label-input') !== null) {
            tagsInput(document.getElementById('label-input'));
            this.inputInitalized = true;
        }
    }
}
ViewResourceCollection.prototype.behaviors = [{behaviorClass: BehaviorTable, table: '#table-resources'}]
ViewResourceCollection.prototype.ui = {
    fileInput: '#file-main_resource_file',
    labelInput: '#label-input'
};
ViewResourceCollection.prototype.events = {
    'change @ui.fileInput': '_handleClickButtonFile'
};
ViewResourceCollection.prototype.filterTitles = {
    'creator__username': 'Creator'
};
