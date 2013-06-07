@import <Foundation/CPObject.j>
@import "../Delegates/ResultsViewPagesDelegate.j"
@import "../Models/SimpleWorkflowRun.j"
@import "../Models/WorkflowRun.j"


/**
 * Runs status delegate that handles the "runs" view.
 */
@implementation ResultsViewRunsDelegate : CPObject
{
    @outlet ResultsViewPagesDelegate        _resultsViewPagesDelegate;
    @outlet CPArrayController               _runsArrayController;
            WorkflowRun                     _currentlySelectedWorkflowRun;
            CPDictionary                    _simpleRunMap;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)setArrayContents:(CPArray)aContents
{
    [_runsArrayController setContent:aContents];
    if ([[_runsArrayController content] count] == 0)
    {
        _currentlySelectedWorkflowRun = nil;
        [_resultsViewPagesDelegate setArrayContents:nil];
    }
}


- (id)init
{
    _simpleRunMap = [[CPDictionary alloc] init];
    return self;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedWorkflowRun = nil;
    [_resultsViewPagesDelegate setArrayContents:nil];
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedWorkflowRun = [[_runsArrayController contentArray] objectAtIndex:rowIndex];
    [_resultsViewPagesDelegate setArrayContents:nil];
    [self handleShouldLoadNotification:nil];
    return YES;
}


/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if (_currentlySelectedWorkflowRun != nil)
    {
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

        // Put the returned data into the dictionary.
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
