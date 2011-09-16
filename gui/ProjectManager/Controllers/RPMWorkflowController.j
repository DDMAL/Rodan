@import <AppKit/CPWindowController.j>

var SharedController2 = nil;

@implementation RPMWorkflowController : CPWindowController
{
    CPWindow window;
    @outlet CPToolbar toolbar;
    @outlet CPObject lol;
    @outlet CPButton button;
}

+(RPMWorkflowController)sharedController
{
    if (!SharedController2)
    {
        SharedController2 = [[RPMWorkflowController alloc] initWithWindowCibName:@"RDWorkflowWindow"];
    }

    return SharedController2;
}

-(void)awakeFromCib
{
    console.log("workflow window woke up");
    console.log(lol);
}

@end