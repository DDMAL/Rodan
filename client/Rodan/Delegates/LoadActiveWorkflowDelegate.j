@global RodanDidLoadWorkflowNotification

/***
    A delegate method for loading the remote workflow from the server.
***/
@implementation LoadActiveWorkflowDelegate : CPObject
{
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   workflowPagesArrayController;
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    // since we're initializing another model for this workflow object,
    // we don't want it to sync back to the server when we create it.
    // so we set it as "Dirt Proof" while it's being created.
    [WLRemoteObject setDirtProof:YES];
    [WorkflowController setActiveWorkflow:[[Workflow alloc] initWithJson:[anAction result]]];
    [WLRemoteObject setDirtProof:NO];

    [currentWorkflowArrayController bind:@"contentArray"
                                    toObject:[WorkflowController activeWorkflow]
                                    withKeyPath:@"workflowJobs"
                                    options:nil];

    [workflowPagesArrayController bind:@"contentArray"
                                  toObject:[WorkflowController activeWorkflow]
                                  withKeyPath:@"pages"
                                  options:nil];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowNotification
                                          object:nil];
}
@end
