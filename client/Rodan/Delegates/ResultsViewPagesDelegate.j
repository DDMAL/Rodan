@import <Foundation/CPObject.j>
@import "../Delegates/ResultsViewResultsDelegate.j"
@import "../Delegates/ResultsViewRunJobsDelegate.j"

@global RodanShouldLoadWorkflowPagesNotification
@global RodanShouldLoadRunJobsNotification
@global RodanShouldLoadWorkflowPageResultsNotification

/**
 * Delegate to handle the pages table in the Results view.
 */
@implementation ResultsViewPagesDelegate : CPObject
{
    @outlet ResultsViewResultsDelegate  _resultsViewResultsDelegate;
    @outlet ResultsViewRunJobsDelegate  _resultsViewRunJobsDelegate;
    @outlet CPArrayController           _pageArrayController;
            Page                        _currentlySelectedPage;
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
                                              name:RodanShouldLoadWorkflowPagesNotification
                                              object:nil];
    }

    return self;
}

- (void)reset
{
    _currentlySelectedPage = nil;
    _associatedWorkflowRun = nil;
    [_pageArrayController setContent:nil];
    [_resultsViewResultsDelegate reset];
    [_resultsViewRunJobsDelegate reset];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedPage = nil;
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedPage = [[_pageArrayController contentArray] objectAtIndex:rowIndex];
    var objectToPass = [[CPObject alloc] init];
    objectToPass.page = _currentlySelectedPage;
    objectToPass.workflowRun = _associatedWorkflowRun;
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadRunJobsNotification
                                          object:objectToPass];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowPageResultsNotification
                                          object:objectToPass];
    return YES;
}

/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    _associatedWorkflowRun = [aNotification object];
    if (_associatedWorkflowRun != nil)
    {
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:[_associatedWorkflowRun pk] + "/?by_page=true"
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
        var workflowRun = [[WorkflowRun alloc] initWithJson:[aAction result]];
        [_pageArrayController setContent:[workflowRun pages]];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
