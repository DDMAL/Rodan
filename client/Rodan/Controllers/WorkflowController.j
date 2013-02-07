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
    @outlet     CPTableView         workflowView;
    @outlet     CPArrayController   workflowArrayController;
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

        // boot up the delegate for the outline view
        [existingWorkflows setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];

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

- (void)removeWorkflow:(id)aSender
{
    var selectedObjects = [workflowArrayController selectedObjects];
    [workflowArrayController removeObjects:selectedObjects];
    [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
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

@end
