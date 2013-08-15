@import <Foundation/CPObject.j>
@import "../Models/ResultsPackage.j"
@import "../Models/WorkflowRun.j"

@global RodanShouldLoadWorkflowResultsPackagesNotification

@global activeUser
@global activeProject

@implementation ResultsPackageController : CPObject
{
    @outlet ResultsViewRunsDelegate _runsDelegate;
    @outlet CPArrayController       _workflowJobsArrayController;
    @outlet CPArrayController       _resultsPackagesArrayController;
    @outlet CPArrayController       _workflowPagesArrayController;
    @outlet CPMatrix                _pageRadioGroup;
    @outlet CPMatrix                _jobRadioGroup;
    @outlet CPRadio                 _pageRadioAll;
    @outlet CPRadio                 _jobRadioAll;
    @outlet CPTableView             _pageTableView;
    @outlet CPTableView             _jobTableView;
    @outlet CPWindow                _createResultsPackageWindow;
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
    [_resultsPackagesArrayController setContent: nil];
    [self handleShouldLoadWorkflowResultsPackagesNotification:nil];
    [CPApp beginSheet:_createResultsPackageWindow
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
 * Handles the create package request.
 */
- (@action)handleCreatePackageRequest:(id)aSender
{
    var resultsPackage = [[ResultsPackage alloc] init];
    [resultsPackage setWorkflowRunUrl:[[_runsDelegate currentlySelectedWorkflowRun] pk]];
    [resultsPackage setCreator:[activeUser pk]];
    if ([_pageRadioGroup selectedRadio] != _pageRadioAll)
    {
        var pageEnumerator = [[self _getSelectedPages] objectEnumerator],
            page = nil,
            pageUrlArray = [[CPMutableArray alloc] init];
        while (page = [pageEnumerator nextObject])
        {
            [pageUrlArray addObject:[page pk]];
        }
        [resultsPackage setPageUrls:pageUrlArray];
    }
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
- (void)handleShouldLoadWorkflowResultsPackagesNotification:(id)aSender
{
    if ([_runsDelegate currentlySelectedWorkflowRun] != nil)
    {
        [self _requestResultsPackages:[_runsDelegate currentlySelectedWorkflowRun]];
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

////////////////////////////////////////////////////////////////////////////////////////////
// Private Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)_requestResultsPackages:(WorkflowRun)aWorkflowRun
{
    var getParameters = @"?workflowrun=" + [aWorkflowRun pk];
    getParameters += @"&creator=" + [activeUser pk];
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:@"/resultspackages/" + getParameters
                    delegate:self
                    message:nil];
}

- (CPArray)_getSelectedPages
{
    var selectedObjects = [[CPArray alloc] init];
    if ([_pageRadioGroup selectedRadio] != _pageRadioAll)
    {
        selectedObjects = [_workflowPagesArrayController selectedObjects];
    }
    return selectedObjects;
}
@end
