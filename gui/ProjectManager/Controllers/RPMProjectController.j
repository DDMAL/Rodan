@import "RPMUsersWindowController.j"
@import "RPMWorkflowController.j"

@implementation RPMProjectController : CPArrayController
{
    @outlet CPOutlineView theView;
    @outlet CPToolbarItem usersToolbarItem;
    @outlet CPToolbarItem workflowToolbarItem;
    @outlet CPToolbarItem projectsToolbarItem;
    @outlet CPToolbarItem testToolbarItem;
    @outlet CPObject test;
}

-(id)init
{
    self = [super init];
    return self;
}

-(id)awakeFromCib
{
    console.log("Waking up project controller");
    console.log(projectsToolbarItem);
    console.log([projectsToolbarItem view]);
    var projectsPopup = [projectsToolbarItem view];
    console.log("Selected project:");
    console.log([projectsPopup indexOfSelectedItem]);
    [usersToolbarItem setTarget:self];
    [usersToolbarItem setAction:@selector(openUsers)];
    
    [workflowToolbarItem setTarget:self];
    [workflowToolbarItem setAction:@selector(openWorkflow)];
}

- (id)openWorkflow
{
    console.log("open workflow window");
    var workflowController = [RPMWorkflowController sharedController];
    [workflowController showWindow:nil];
}

-(id)openUsers
{
    console.log("clicked lol");
    var usersWindowController = [RPMUsersWindowController sharedController];
    [usersWindowController showWindow:nil];
}

@end
