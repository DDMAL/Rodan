@import <Foundation/CPObject.j>
@import "../Models/Result.j"
@import "../Models/Page.j"
@import "../Models/WorkflowRun.j"

@global RodanShouldLoadWorkflowPageResultsNotification

/**
 * Delegate to handle the results table in the Results view.
 */
@implementation ResultsViewResultsDelegate : CPObject
{
    @outlet CPArrayController   _resultArrayController;
            Result              _currentlySelectedResult;
            Page                _associatedPage;
            WorkflowRun         _associatedWorkflowRun;
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
                                              name:RodanShouldLoadWorkflowPageResultsNotification
                                              object:nil];
    }

    return self;
}

- (void)reset
{
    _currentlySelectedResult = nil;
    _associatedPage = nil
    _associatedWorkflowRun = nil;
    [_resultArrayController setContent:nil];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Initializes packaging of results.
 */
- (void)returnResults:(CPString)aResult
{
    window.open(aResult, "_blank");
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedResult = nil;
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedResult = [[_resultArrayController contentArray] objectAtIndex:rowIndex];
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
                        path:@"/results/?workflowrun=" + [_associatedWorkflowRun uuid] + "&page=" + [_associatedPage uuid]
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
        [_resultArrayController setContent: [Result objectsFromJson: [aAction result]]];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
