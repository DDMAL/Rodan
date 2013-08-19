@import <Foundation/CPObject.j>
@import "../Models/Page.j"
@import "../Models/RunJob.j"
@import "../Models/WorkflowRun.j"

@global RodanShouldLoadRunJobsNotification

/**
 * Delegate to handle the run jobs table in the Results view.
 */
@implementation ResultsViewRunJobsDelegate : CPObject
{
    @outlet CPArrayController           _runJobArrayController;
    @outlet InteractiveJobsController   _interactiveJobsController;
            RunJob                      _currentlySelectedRunJob;
            Page                        _associatedPage;
            WorkflowRun                 _associatedWorkflowRun;
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
                                              name:RodanShouldLoadRunJobsNotification
                                              object:nil];
    }

    return self;
}

- (void)reset
{
    _currentlySelectedRunJob = nil;
    _associatedPage = nil
    _associatedWorkflowRun = nil;
    [_runJobArrayController setContent:nil];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedRunJob = nil;
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedRunJob = [[_runJobArrayController contentArray] objectAtIndex:rowIndex];
    return YES;
}

/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if ([aNotification object] != nil)
    {
        _associatedPage = [aNotification object].page,
        _associatedWorkflowRun = [aNotification object].workflowRun;
    }

    if (_associatedPage != nil && _associatedWorkflowRun != nil)
    {
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:@"/runjobs/?workflowrun=" + [_associatedWorkflowRun uuid] + "&page=" + [_associatedPage uuid]
                        delegate:self
                        message:nil];
    }
}

/**
 * Handles success of loading.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result] && _associatedPage != nil && _associatedWorkflowRun != nil)
    {
        [WLRemoteObject setDirtProof:YES];
        [_runJobArrayController setContent: [RunJob objectsFromJson: [aAction result]]];
        [WLRemoteObject setDirtProof:NO];
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
// Action Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Attempts interactive job.
 */
- (@action)displayInteractiveJobWindow:(id)aSender
{
    var runJob = [[_runJobArrayController selectedObjects] objectAtIndex:0];
    [_interactiveJobsController runInteractiveRunJob:runJob fromSender:aSender];
}

- (@action)displayErrorDetails:(id)aSender
{
    var runJob = [[_runJobArrayController selectedObjects] objectAtIndex:0],
        alert = [[CPAlert alloc] init];
    [alert setMessageText:[runJob errorDetails]];
    [alert runModal];
}
/*
/**
 * Attempts retry of failed runjobs for selected run.
 *//*
- (@action)retryFailedRunJobs:(id)aSender
{
    [WLRemoteAction schedule:WLRemoteActionPatchType
                    path:[_currentlySelectedWorkflowRun pk]
                    delegate:null
                    message:null];
}*/
@end
