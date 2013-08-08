@import <Foundation/CPObject.j>

@global RodanShouldLoadWorkflowJobsNotification

/**
 * Delegate to handle the workflow job loading.
 */
@implementation ResultsViewWorkflowJobsDelegate : CPObject
{
    @outlet CPArrayController   _workflowJobsArrayController;
            Workflow            _associatedWorkflow;
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
                                              name:RodanShouldLoadWorkflowJobsNotification
                                              object:nil];
    }

    return self;
}

- (void)reset
{
    _associatedWorkflow = nil;
    [_associatedWorkflow setContent:nil];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
}

/**
 * Handles the request to load.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    if ([WorkflowController activeWorkflow] != nil)
    {
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:@"/workflowjobs/?workflow=" + [[WorkflowController activeWorkflow] uuid]
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
        [_workflowJobsArrayController setContent: [WorkflowJob objectsFromJson:[aAction result]]];
        [WLRemoteObject setDirtProof:NO];
    }
}
@end
