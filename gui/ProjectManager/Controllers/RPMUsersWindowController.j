@import <AppKit/CPWindowController.j>
@import "DjangoAPIController.j"

var SharedController = nil;

@implementation RPMUsersWindowController : CPWindowController
{
    @outlet CPToolbar toolbar;
    CPWindow window;
    @outlet CPToolbarItem addUserIcon;
    @outlet CPToolbarItem addGroupIcon;
    @outlet CPToolbarItem deleteUserIcon;
    @outlet CPToolbarItem deleteGroupIcon;
    @outlet CPView addUserView;
    @outlet CPView addGroupView;
    CPPanel addGroupPanel;
    CPPanel addUserPanel;
    CPTableColumn leftColumn;
}

+(RPMUsersWindowController)sharedController
{
    if (!SharedController)
    {
        SharedController = [[RPMUsersWindowController alloc] initWithWindowCibName:@"RDUsersGroupsWindow"];
        console.log(SharedController);
    }

    return SharedController;
}

-(void)awakeFromCib
{
    console.log(toolbar);
    console.log("users window woke up");
    [addUserIcon setTarget:self];
    [addUserIcon setAction:@selector(showAddUserSheet)];
    [addGroupIcon setTarget:self];
    [addGroupIcon setAction:@selector(showAddGroupSheet)];

    // Start in "view users" mode
    console.log([window subviews]);
}

- (void)showAddUserSheet
{
    // First clear the string values
    var subviews = [addUserView subviews];
    for (var i = 0; i < 7; i += 2) {
        [subviews[i] setStringValue:@""];
    }
    console.log("lol showing add user sheet");
    // Doing this programmatically because having to restart every time I want to add an outlet to the xib is not fun
    var addUserPanel = [[CPPanel alloc] initWithContentRect:CGRectMake(0, 0, 270, 175) styleMask:CPClosableWindowMask];
    [addUserPanel setFloatingPanel:YES];
    [addUserPanel orderFront:self];
    [addUserPanel center];
    [addUserPanel setContentView:addUserView];
    var addUserButton = [[CPButton alloc] initWithFrame:CGRectMake(110, 145, 80, 24)];
    [addUserButton setTitle:@"Go"];
    [addUserButton setTarget:self];
    [addUserView addSubview:addUserButton];
    [addUserPanel setDefaultButton:addUserButton];
    // Since Objective-J doesn't seem to let me pass actual arguments using @selector ...
    [addUserButton setAction:@selector(addUser)];
}

- (void)showAddGroupSheet
{
    console.log("lol showing add group sheet");
    var addGroupPanel = [[CPPanel alloc] initWithContentRect:CGRectMake(0, 0, 300, 90) styleMask:CPClosableWindowMask];
    [addGroupPanel setFloatingPanel:YES];
    [addGroupPanel orderFront:self];
    [addGroupPanel center];
    [addGroupPanel setContentView:addGroupView];
    var addGroupButton = [[CPButton alloc] initWithFrame:CGRectMake(110, 60, 80, 24)];
    [addGroupButton setTitle:@"Go"];
    [addGroupButton setTarget:self];
    [addGroupButton setAction:@selector(addGroup)];
    [addGroupView addSubview:addGroupButton];
    [addGroupPanel setDefaultButton:addGroupButton];
}

- (void)addUser
{
    console.log("ADD THIS USER NOW");
    // Please don't make me try to connect more outlets in Interface Builder even subviews are better than that
    var subviews = [addUserView subviews];
    var newUser = {
        email: [subviews[0] stringValue],
        institution: [subviews[2] stringValue],
        real_name: [subviews[4] stringValue],
        username: [subviews[6] stringValue],
    }
    
    var numErrors = 0;
    // Make sure they all have values ... (clean this code up later)
    if (newUser.email == '')
    {
        [subviews[0] setPlaceholderString:@"You must enter an email"];
        numErrors++;
    }
    if (newUser.institution == '')
    {
        [subviews[2] setPlaceholderString:@"You must enter an institution"];
        numErrors++;
    }
    if (newUser.real_name == '')
    {
        [subviews[4] setPlaceholderString:@"You must enter a real name"];
        numErrors++;
    }
    if (newUser.username == '')
    {
        [subviews[6] setPlaceholderString:@"You must enter a username"];
        numErrors++;
    }
    if (numErrors == 0) {
        [[DjangoAPIController sharedController] addUserWithObject:newUser];
        [addUserPanel orderOut:self];
    }
}

- (void)addGroup
{
    console.log("ADD THIS GROUP NOW");
}

@end