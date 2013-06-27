@global RodanDidLoadWorkflowNotification

/***
    A delegate method for loading the remote workflow from the server.
***/
@implementation LoadActiveWorkflowDelegate : CPObject
{
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   workflowPagesArrayController;
    @outlet     WorkflowController  workflowController;
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    var workflow = [workflowController updateWorkflowWithJson:[anAction result]];
    if (workflow !== nil)
    {
        [currentWorkflowArrayController bind:@"contentArray"
                                        toObject:workflow
                                        withKeyPath:@"workflowJobs"
                                        options:nil];

        [workflowPagesArrayController bind:@"contentArray"
                                      toObject:workflow
                                      withKeyPath:@"pages"
                                      options:nil];

        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowNotification
                                              object:nil];
    }
}
@end
