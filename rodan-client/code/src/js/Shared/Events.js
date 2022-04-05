/**
 * Backbone.Radio events use in this GUI.
 */
var GUI_EVENTS = 
{
    REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW: 'REQUEST__WORKFLOWBUILDER_GUI_GET_WORKFLOW',
    EVENT__WORKFLOWBUILDER_GUI_DESTROY: 'EVENT__WORKFLOWBUILDER_GUI_DESTROY',                           // Called when WorkflowBuilder has been destroyed.
    REQUEST__WORKFLOWBUILDER_GUI_ZOOM_IN: 'REQUEST__WORKFLOWBUILDER_GUI_ZOOM_IN',                                                   // Called when request workspace zoom in.
    REQUEST__WORKFLOWBUILDER_GUI_ZOOM_OUT: 'REQUEST__WORKFLOWBUILDER_GUI_ZOOM_OUT',                                                 // Called when request workspace zoom out.
    REQUEST__WORKFLOWBUILDER_GUI_ZOOM_RESET: 'REQUEST__WORKFLOWBUILDER_GUI_ZOOM_RESET',                                             // Called when request workspace zoom reset.
    REQUEST__WORKFLOWBUILDER_GUI_ADD_RESOURCEDISTRIBUTOR: 'REQUEST__WORKFLOWBUILDER_GUI_ADD_RESOURCEDISTRIBUTOR',
    REQUEST__WORKFLOWBUILDER_GUI_GET_SELECTED_WORKFLOWJOBS: 'REQUEST__WORKFLOWBUILDER_GUI_GET_SELECTED_WORKFLOWJOBS'         // Called when request list of all selected WorkflowJob IDs.
};

export default GUI_EVENTS;