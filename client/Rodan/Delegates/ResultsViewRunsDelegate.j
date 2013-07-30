@import <Foundation/CPObject.j>
@import "../Controllers/InteractiveJobsController.j"
@import "../Delegates/ResultsViewPagesDelegate.j"
@import "../Models/WorkflowRun.j"


@global RodanShouldLoadWorkflowRunsNotification
@global RodanShouldLoadWorkflowPagesNotification


/**
 * Runs status delegate that handles the "runs" view.
 */
@implementation ResultsViewRunsDelegate : CPObject
{
    @outlet InteractiveJobsController       _interactiveJobsController;
    @outlet ResultsViewPagesDelegate        _resultsViewPagesDelegate;
    @outlet CPArrayController               _runsArrayController;
            WorkflowRun                     _currentlySelectedWorkflowRun;
            CPString                        _workflowUUID;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (id)init
{
    self = [super init];
    if (self)
    {
        [[CPNotificationCenter defaultCenter] addObserver:self
                                              selector:@selector(handleShouldLoadNotification:)
                                              name:RodanShouldLoadWorkflowRunsNotification
                                              object:nil];
    }

    return self;
}

- (void)reset
{
    _currentlySelectedWorkflowRun = nil;
    _workflowUUID = nil;
    [_runsArrayController setContent:nil];
    [_resultsViewPagesDelegate reset];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedWorkflowRun = nil;
    [_resultsViewPagesDelegate reset];
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedWorkflowRun = [[_runsArrayController contentArray] objectAtIndex:rowIndex];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowPagesNotification
                                          object:_currentlySelectedWorkflowRun];
    return YES;
}

/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if ([aNotification object] != nil)
    {
        _workflowUUID = [aNotification object];
    }

    if (_workflowUUID != nil)
    {
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:@"/workflowruns/?workflow=" + _workflowUUID
                        delegate:self
                        message:nil];
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
        var workflowRunsArray = [WorkflowRun objectsFromJson:[aAction result]];
        [_runsArrayController setContent:workflowRunsArray];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
