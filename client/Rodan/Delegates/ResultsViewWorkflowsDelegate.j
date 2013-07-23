@import <Foundation/CPObject.j>
@import "../Controllers/WorkflowController.j"
@import "../Delegates/ResultsViewRunsDelegate.j"
@import "../Models/Workflow.j"


@global RodanShouldLoadWorkflowResultsWorkflowRunsNotification
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
                                          selector:@selector(handleShouldLoadNotification:)
                                          name:RodanShouldLoadWorkflowResultsWorkflowRunsNotification
                                          object:nil];
    return self;
}

- (void)reset
{
    [_resultsViewRunsDelegate setArrayContents:nil];
    _currentlySelectedWorkflow = [WorkflowController activeWorkflow];
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    [_resultsViewRunsDelegate setArrayContents:nil];
    _currentlySelectedWorkflow = nil;
    [WorkflowController setActiveWorkflow:_currentlySelectedWorkflow];
}


- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedWorkflow = [[_workflowArrayController contentArray] objectAtIndex:rowIndex];
    [WorkflowController setActiveWorkflow:_currentlySelectedWorkflow];
    [_resultsViewRunsDelegate setArrayContents:nil];
    [self handleShouldLoadNotification:nil];
    return YES;
}


/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if (_loadingWorkflow == nil && _currentlySelectedWorkflow != nil)
    {
        _loadingWorkflow = _currentlySelectedWorkflow;
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:[_loadingWorkflow remotePath]
                        delegate:self
                        message:"Loading Workflow"];
    }
}


/**
 * Handles success of loading.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];
        [_loadingWorkflow initWithJson:[aAction result]];
        [_resultsViewRunsDelegate setArrayContents:[_currentlySelectedWorkflow workflowRuns]];
        _loadingWorkflow = nil;
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
