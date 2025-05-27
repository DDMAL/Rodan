// import $ from 'jquery';
// import _ from 'underscore';
// import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
// import Marionette from 'backbone.marionette';
// import Radio from 'backbone.radio';

// /**
//  * This is a layout to help render a Collection and a single item.
//  * We're using a LayoutView as opposed to a CompositeView because the single model
//  * that would be associated with the CompositveView is not initially known, so it can't
//  * rerender.
//  */
// export default class LayoutViewModel extends Marionette.View
// {
// ///////////////////////////////////////////////////////////////////////////////////////
// // PUBLIC METHODS
// ///////////////////////////////////////////////////////////////////////////////////////
//     /**
//      * Initializes the instance.
//      */
//     initialize()
//     {
//         console.log(this);
//         this.setElement('<div id="region-main-content-wrapper" class="content-wrapper column-content"></div>');
//         this.addRegions({
//             regionCollection: '#region-main_layoutview_model_collection',
//             regionProjectInfo: '#region-main_layoutview_model_item',
//             regionCollectionItemInfo: '#region-main_layoutview_model_collection_item'
//         });
//     }

//     /**
//      * Show a Collection view.
//      *
//      * @param {Marionette.View} view Collection view to show
//      */
//     showCollection(view)
//     {
//         console.log(view);
//         this.showChildView('regionCollection', view);
//     }

//     /**
//      * Show an item view.
//      *
//      * @param {Marionette.View} view item view to show
//      */
//     showItem(view)
//     {
//         console.log(view);
//         this.showChildView('regionProjectInfo', view);
//     }

//     /**
//      * Show an item view. This is for the secondary item view.
//      * 
//      * @param {Marionette.View} view item view to show
//      */
//     showSecondaryItem(view) {
//         this.showChildView('regionCollectionItemInfo', view);
//     }

//     /**
//      * Clears item view.
//      */
//     clearItemView()
//     {
//         this.getRegion('regionCollectionItemInfo').empty();
//     }

//     /**
//      * Handle RunJob button.
//      */
//     _handleButtonRunJobs()
//     {
//         Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RUNJOB_SELECTED_COLLECTION, {project: this.model});
//     }

//     /**
//      * Handle click resource count.
//      */
//     _handleClickResourceCount()
//     {
//         console.log(this);
//         Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCE_SELECTED_COLLECTION, {project: this.model});
//     }

//     /**
//      * Handle click workflow count.
//      */
//     _handleClickWorkflowCount()
//     {
//         Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__WORKFLOW_SELECTED_COLLECTION, {project: this.model});
//     }

//     /**
//      * Handle click button ResourceLists.
//      */
//     _handleButtonResourceLists()
//     {
//         Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__RESOURCELIST_SELECTED_COLLECTION, {project: this.model});
//     }

//     /**
//      * Handle button Project users.
//      */
//     _handleButtonProjectUsers()
//     {
//         Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__PROJECT_USERS_SELECTED, {project: this.model});
//     }
// }


// LayoutViewModel.prototype.ui = {
//     // buttonResourceLists: '#button-resourcelists',
//     resourceCount: '#resource_count',
//     workflowCount: '#workflow_count',
//     buttonRunJobs: '#button-runjobs',
//     buttonUsers: '#button-project_users'
// };

// LayoutViewModel.prototype.events = {
//     'click @ui.resourceCount': '_handleClickResourceCount',
//     'click @ui.workflowCount': '_handleClickWorkflowCount',
//     'click @ui.buttonRunJobs': '_handleButtonRunJobs',
//     'click @ui.buttonResourceLists': '_handleButtonResourceLists',
//     'click @ui.buttonUsers': '_handleButtonProjectUsers'
// };

// LayoutViewModel.prototype.template = _.template($('#template-main_layoutview_model').text());
