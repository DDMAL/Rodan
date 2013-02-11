@import <Foundation/CPObject.j>
@import <AppKit/CPArrayController.j>
@import <AppKit/CPBrowser.j>
@import <AppKit/CPOutlineView.j>
@import <AppKit/CPTableView.j>

@import "../Models/Workflow.j"

@global activeProject;
@global RodanDidLoadWorkflowsNotification;
@global RodanWorkflowTreeNeedsRefresh;

@implementation WorkflowController : CPObject
{
    @outlet     CPBrowser           jobBrowser;
    @outlet     CPTableView         existingWorkflows;
    @outlet     CPTableView         availableJobs;

    @outlet     CPTableView         workflowView;
    @outlet     CPArrayController   workflowArrayController;

                CPImage             workflowIcon;
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
        [existingWorkflows setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
        [availableJobs setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowsNotification
                                              object:[anAction result]];
    }
}

- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (IBAction)saveWorkflow:(id)aSender
{
    CPLog("Save Workflow");
}

- (IBAction)addImagesToWorkflow:(id)aSender
{
    CPLog("Add Image to Workflow");
}

- (IBAction)editWorkflow:(id)aSender
{
    CPLog("Edit Workflow");
}

- (IBAction)stopWorkflow:(id)aSender
{
    CPLog("Stop Workflow");
}

- (IBAction)loadJobsForWorkflow:(id)aSender
{
    var selectionIndex = [workflowArrayController selectionIndex];
    console.log(selectionIndex);
    if (selectionIndex != -1)
    {
        var workflow = [[workflowArrayController contentArray] objectAtIndex:selectionIndex];

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
    [wflow setProject:[activeProject pk]];
    [workflowArrayController addObject:wflow];
    [wflow ensureCreated];
}

- (void)newWorkflowGroup:(id)aSender
{
    CPLog("In the workflow controller");
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
