@import <AppKit/AppKit.j>

@implementation NewProjectController : CPObject
{
    @outlet     CPWindow    theWindow;
    @outlet     CPTextField projectName;
    @outlet     CPTextField projectDescription;
}

- (IBAction)saveProject:(id)aSender
{
    CPLog("Save Project");
}

@end
