@import <AppKit/AppKit.j>

@implementation ProjectController : CPObject
{
    @outlet     CPWindow    theWindow;
    @outlet     CPTextField projectName;
    @outlet     CPTextField projectDescription;
}

- (IBAction)saveProject:(id)aSender
{
    CPLog("Save Project");
}

- (IBAction)openProject:(id)aSender
{
    CPLog("Open Project");
}

@end
