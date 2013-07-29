@import <Foundation/CPObject.j>
@import "../Models/Result.j"

@global RodanShouldLoadWorkflowPageResultsNotification

/**
 * Delegate to handle the results table in the Results view.
 */
@implementation ResultsViewResultsDelegate : CPObject
{
    @outlet CPArrayController   _resultArrayController;
            Result              _currentlySelectedResult;
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
    var page = [aNotification object].page,
        workflowRun = [aNotification object].workflowRun;
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:@"/results/?workflowrun=" + [workflowRun uuid] + "&page=" + [page uuid]
                    delegate:self
                    message:nil];
}

/**
 * Handles success of loading.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];
        [_resultArrayController setContent: [Result objectsFromJson: [aAction result]]];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
