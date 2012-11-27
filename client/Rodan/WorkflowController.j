@import <AppKit/AppKit.j>

@implementation WorkflowController : CPObject
{
    @outlet     CPWindow    newWorkflowWindow;
    @outlet     CPTextField projectName;
}

- (IBAction)saveWorkflow:(id)aSender
{
    CPLog("Save Workflow");
}

@end
