@import <Foundation/CPObject.j>
@import "../Controllers/WorkflowController.j"
@import "../Models/Workflow.j"

@global activeProject
@global RodanShouldLoadWorkflowsNotification
@global RodanShouldLoadWorkflowRunsNotification

@class WorkflowController

/**
 * Delegate for the Workflow table view in the Results view.
 */
@implementation ResultsViewWorkflowsDelegate : CPObject
{
    @outlet     CPArrayController       _workflowArrayController;
    @outlet     ResultsViewRunsDelegate _resultsViewRunsDelegate;
                Workflow                _currentlySelectedWorkflow;
                Workflow                _loadingWorkflow;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (id)init
{
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(handleShouldLoadWorkflowsNotification:)
                                          name:RodanShouldLoadWorkflowsNotification
                                          object:nil];
    return self;
}

- (void)reset
{
    [_resultsViewRunsDelegate reset];
    _currentlySelectedWorkflow = [WorkflowController activeWorkflow];
}

/**
 * Does a workflow load request.
 */
- (void)sendLoadRequest
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:@"/workflows/?project=" + [activeProject uuid]
                    delegate:self
                    message:nil];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedWorkflow = nil;
    [WorkflowController setActiveWorkflow:nil];
    [_resultsViewRunsDelegate reset];
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedWorkflow = [[_workflowArrayController contentArray] objectAtIndex:rowIndex];
    [WorkflowController setActiveWorkflow:_currentlySelectedWorkflow];
    [_resultsViewRunsDelegate reset];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowRunsNotification
                                          object:[_currentlySelectedWorkflow uuid]];
    return YES;
}

/**
 * Handles workflows load notification.
 */
- (void)handleShouldLoadWorkflowsNotification:(CPNotification)aNotification
{
    [self sendLoadRequest];
}

/**
 * Handles remote object load.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];
        var workflowArray = [Workflow objectsFromJson:[aAction result]];
        [_workflowArrayController setContent:workflowArray];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
