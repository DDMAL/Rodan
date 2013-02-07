@import <Foundation/CPObject.j>
@import <AppKit/CPBrowser.j>
@import <AppKit/CPOutlineView.j>
@import <AppKit/CPTableView.j>

@import "../Models/Workflow.j"

@global activeProject;

@implementation WorkflowController : CPObject
{
    @outlet     CPBrowser       jobBrowser;
    @outlet     CPOutlineView   existingWorkflows;
    @outlet     CPTableView     workflowView;
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

- (void)newWorkflow:(id)aSender
{
    var wflow = [[Workflow alloc] init];
    console.log(activeProject);
    [wflow setProject:[activeProject pk]];
    [wflow ensureCreated];
    console.log(wflow);
}

- (void)newWorkflowGroup:(id)aSender
{
    CPLog("In the workflow controller");
}

@end
