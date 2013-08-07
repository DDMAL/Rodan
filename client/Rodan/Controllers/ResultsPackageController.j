@import <Foundation/CPObject.j>
@import "../Models/ResultsPackage.j"
@import "../Models/WorkflowRun.j"

@global RodanShouldLoadWorkflowResultsPackagesNotification

@global activeUser
@global activeProject

@implementation ResultsPackageController : CPObject
{
    @outlet ResultsViewRunsDelegate _runsDelegate;
    @outlet CPArrayController       _resultsPackageJobArrayController;
    @outlet CPArrayController       _resultsPackagePageArrayController;
    @outlet CPArrayController       _workflowJobsArrayController;
    @outlet CPArrayController       _resultsPackagesArrayController;
    @outlet CPMatrix                _pageRadioGroup;
    @outlet CPMatrix                _jobRadioGroup;
    @outlet CPRadio                 _pageRadioAll;
    @outlet CPRadio                 _jobRadioAll;
    @outlet CPTableView             _pageTableView;
    @outlet CPTableView             _jobTableView;
    @outlet CPWindow                _createResultsPackageWindow;
    @outlet CPWindow                _listResultsPackageWindow;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Init Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (id)init
{
    self = [super init];
    if (self)
    {
        [[CPNotificationCenter defaultCenter] addObserver:self
                                              selector:@selector(handleShouldLoadWorkflowResultsPackagesNotification:)
                                              name:RodanShouldLoadWorkflowResultsPackagesNotification
                                              object:nil];
    }

    return self;
}

- (void)awakeFromCib
{
}

////////////////////////////////////////////////////////////////////////////////////////////
// Action Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Opens the create results package window.
 */
- (@action)openCreateResultsPackageWindow:(id)aSender
{
    [CPApp beginSheet:_createResultsPackageWindow
           modalForWindow:[CPApp mainWindow]
           modalDelegate:self
           didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

/**
 * Opens the list results package window.
 */
- (@action)openListResultsPackageWindow:(id)aSender
{
    [CPApp beginSheet:_listResultsPackageWindow
           modalForWindow:[CPApp mainWindow]
           modalDelegate:self
           didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

/**
 * Closes the create results package window.
 */
- (@action)closeCreateResultsPackageWindow:(id)aSender
{
    [CPApp endSheet:_createResultsPackageWindow returnCode:[aSender tag]];
}

/**
 * Closes the list results package window.
 */
- (@action)closeListResultsPackageWindow:(id)aSender
{
    [CPApp endSheet:_listResultsPackageWindow returnCode:[aSender tag]];
}

/**
 * Handles the create package request.
 */
- (@action)handleCreatePackageRequest:(id)aSender
{
    var resultsPackage = [[ResultsPackage alloc] init];
    [resultsPackage setWorkflowRun:[_runsDelegate currentlySelectedWorkflowRun]];
    [resultsPackage setCreator:[activeUser pk]];
    [resultsPackage ensureCreated];
}

/**
 * Handles page radio button action.
 */
- (@action)handlePageRadioAction:(id)aSender
{
    [_pageTableView setEnabled: [_pageRadioGroup selectedRadio] != _pageRadioAll];
    return YES;
}

/**
 * Handles job radio button action.
 */
- (@action)handleJobRadioAction:(id)aSender
{
    [_jobTableView setEnabled: [_jobRadioGroup selectedRadio] == _jobRadioAll];
    return YES;
}

/**
 * Handles download of results package.
 */
- (@action)handleDownload:(id)aSender
{
    if ([[_resultsPackagesArrayController selectedObjects] count] > 0)
    {
        var resultsPackage = [[_resultsPackagesArrayController selectedObjects] objectAtIndex:0];
        if ([resultsPackage percentCompleted] == 100)
        {
            window.open([resultsPackage downloadUrl], "_blank");
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Handles the request to load.
 */
- (void)handleShouldLoadWorkflowJobsNotification:(CPNotification)aNotification
{
    if ([aNotification object] != nil)
    {
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:@"/workflowjobs/?workflow=" + [aNotification object]
                        delegate:self
                        message:nil];
    }
}

- (void)handleShouldLoadWorkflowResultsPackagesNotification:(id)aSender
{
    if ([_runsDelegate currentlySelectedWorkflowRun] != nil)
    {
        var getParameters = @"?workflowrun=" + [[_runsDelegate currentlySelectedWorkflowRun] pk];
        getParameters += @"&creator=" + [activeUser pk];
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:@"/resultspackages/" + getParameters
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
        [_resultsPackagesArrayController setContent: [ResultsPackage objectsFromJson:[aAction result]]];
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
@end
