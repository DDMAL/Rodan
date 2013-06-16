@import <Foundation/CPObject.j>
@import "../Controllers/InteractiveJobsController.j"
@import "../Delegates/ResultsViewPagesDelegate.j"
@import "../Models/SimpleWorkflowRun.j"
@import "../Models/WorkflowRun.j"


@global RodanShouldLoadWorkflowResultsWorkflowResultsNotification


/**
 * Runs status delegate that handles the "runs" view.
 */
@implementation ResultsViewRunsDelegate : CPObject
{
    @outlet InteractiveJobsController       _interactiveJobsController;
    @outlet ResultsViewPagesDelegate        _resultsViewPagesDelegate;
    @outlet CPArrayController               _runsArrayController;
    @outlet CPArrayController               _runJobArrayController;
            WorkflowRun                     _currentlySelectedWorkflowRun;
            int                             _currentlySelectedRowIndex;
            CPDictionary                    _simpleRunMap;
            WorkflowRun                     _loadingWorkflowRun;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)setArrayContents:(CPArray)aContents
{
    // Do a reset and check if we were filled.
    [_runsArrayController setContent:aContents];
    if ([[_runsArrayController content] count] == 0)
    {
        _currentlySelectedRowIndex = -1;
        [_resultsViewPagesDelegate setArrayContents:nil];
        [_runJobArrayController setContent: nil];
    }
    [self _repointCurrentlySelectedObject];

    // If something is currently selected, we should updated run jobs.
    if (_currentlySelectedRowIndex >= 0)
    {
        [_runJobArrayController setContent: [_currentlySelectedWorkflowRun runJobs]];
    }
}

- (id)init
{
    self = [super init];
    if (self)
    {
        _currentlySelectedRowIndex = -1;
        _simpleRunMap = [[CPDictionary alloc] init];
        [[CPNotificationCenter defaultCenter] addObserver:self
                                              selector:@selector(handleShouldLoadNotification:)
                                              name:RodanShouldLoadWorkflowResultsWorkflowResultsNotification
                                              object:nil];
    }

    return self;
}

/**
 * Attempts interactive job.
 */
- (@action)displayInteractiveJobWindow:(id)aSender
{
    var runJob = [[_runJobArrayController selectedObjects] objectAtIndex:0];
    [_interactiveJobsController runInteractiveRunJob:runJob fromSender:aSender];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Private Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Repoints the currently selected object.
 */
- (void)_repointCurrentlySelectedObject
{
    if (_currentlySelectedRowIndex >= 0)
    {
        _currentlySelectedWorkflowRun = [[_runsArrayController contentArray] objectAtIndex:_currentlySelectedRowIndex];
    }
    else
    {
        _currentlySelectedWorkflowRun = nil;
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    // Update ourselves.
    _currentlySelectedRowIndex = -1;
    [self _repointCurrentlySelectedObject];
    [_runJobArrayController setContent: nil];

    // Inform others.
    [_resultsViewPagesDelegate setArrayContents:nil];
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    // Update ourselves.
    _currentlySelectedRowIndex = rowIndex;
    [self _repointCurrentlySelectedObject];
    [_runJobArrayController setContent: [_currentlySelectedWorkflowRun runJobs]];
    [self handleShouldLoadNotification:nil];

    // Inform others.
    [_resultsViewPagesDelegate setArrayContents:nil];

    return YES;
}

/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if (_loadingWorkflowRun == nil && _currentlySelectedWorkflowRun != nil)
    {
        _loadingWorkflowRun = _currentlySelectedWorkflowRun;
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:[_currentlySelectedWorkflowRun pk] + @"?by_page=true"  // return results by page, rather than by run_job
                        delegate:self
                        message:"Loading Workflow Run Results"];
    }
}

/**
 * Handles remote object load.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];

        // Update the loading object.
        [_loadingWorkflowRun initWithJson:[aAction result]];
        _loadingWorkflowRun = nil;

        // Get the key.
        var simpleRun = [[SimpleWorkflowRun alloc] initWithJson:[aAction result]],
            key = [simpleRun pk],
            splitString = [key componentsSeparatedByString:"/"];
        if ([splitString count] > 1)
        {
            key = [splitString objectAtIndex:([splitString count] - 2)];
        }

        // Only put if the run was updated.
        if ([_simpleRunMap valueForKey:key] == nil || [simpleRun updated] != [[_simpleRunMap valueForKey:key] updated])
        {
            [_simpleRunMap setValue:simpleRun forKey:key];
        }

        // Reload the pages for the currently selected run.
        if (_currentlySelectedWorkflowRun != nil)
        {
            key = [_currentlySelectedWorkflowRun pk];
            splitString = [key componentsSeparatedByString:"/"];
            if ([splitString count] > 1)
            {
                key = [splitString objectAtIndex:([splitString count] - 2)];
            }
            [_resultsViewPagesDelegate setArrayContents:[[_simpleRunMap valueForKey:key] pages]];
        }
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
