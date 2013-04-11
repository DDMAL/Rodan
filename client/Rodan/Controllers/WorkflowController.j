@import <Foundation/CPObject.j>
@import "../Models/Workflow.j"

@global activeProject;
@global RodanDidLoadWorkflowsNotification;
@global RodanWorkflowTreeNeedsRefresh;


@implementation WorkflowController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
    @outlet     CPArrayController       jobArrayController;
}

- (void)fetchWorkflows
{
    [WLRemoteAction schedule:WLRemoteActionGetType path:"/workflows" delegate:self message:"Loading jobs"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    if ([anAction result])
    {
        var j = [Workflow objectsFromJson:[anAction result]];
        [workflowArrayController addObjects:j];

        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowsNotification
                                      object:[anAction result]];
    }
}

- (void)removeWorkflow:(id)aSender
{
    if ([workflowArrayController selectedObjects])
    {
        var alert = [CPAlert alertWithMessageText:@"You are about to permanently delete this workflow"
                             defaultButton:@"Delete"
                             alternateButton:@"Cancel"
                             otherButton:nil
                             informativeTextWithFormat:nil];
        [alert setDelegate:self];
        [alert runModal];
    }
}

- (void)newWorkflow:(id)aSender
{
    var wflow = [[Workflow alloc] init];
    [wflow setProjectURL:[activeProject pk]];
    [workflowArrayController addObject:wflow];
    [wflow ensureCreated];
}

- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    if (returnCode == 0)
    {
        var selectedObjects = [workflowArrayController selectedObjects];
        [workflowArrayController removeObjects:selectedObjects];
        [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
    }
}

- (void)emptyWorkflowArrayController
{
    [[workflowArrayController contentArray] removeAllObjects];
}

@end
