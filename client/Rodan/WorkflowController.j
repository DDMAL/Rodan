@import <AppKit/AppKit.j>

@implementation WorkflowController : CPObject
{
    @outlet     CPWindow    newWorkflowWindow;
    @outlet     CPWindow    addImageWindow;
    @outlet     CPTextField projectName;
}

- (IBAction)saveWorkflow:(id)aSender
{
    CPLog("Save Workflow");
    [newWorkflowWindow close];
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

@end
