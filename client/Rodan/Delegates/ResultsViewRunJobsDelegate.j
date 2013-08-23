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
    @outlet CPArrayController           _runJobSettingsArrayController;
    @outlet InteractiveJobsController   _interactiveJobsController;
    @outlet CPWindow                    _viewJobSettingsWindow;
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
    [_runJobSettingsArrayController setContent:nil];
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
    [_runJobSettingsArrayController setContent:[_currentlySelectedRunJob jobSettingsArray]];
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

/**
 * Handler for window close.
 */
- (void)didEndSheet:(CPWindow)aSheet returnCode:(int)returnCode contextInfo:(id)contextInfo
{
    [aSheet orderOut:self];
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

- (@action)openViewJobSettingsWindow:(id)aSender
{
    [CPApp beginSheet:_viewJobSettingsWindow
           modalForWindow:[CPApp mainWindow]
           modalDelegate:self
           didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

/**
 * Closes the create results package window.
 */
- (@action)closeViewJobSettingsWindow:(id)aSender
{
    [CPApp endSheet:_viewJobSettingsWindow returnCode:[aSender tag]];
}
@end
