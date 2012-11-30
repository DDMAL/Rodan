/*
 * AppController.j
 * Rodan
 *
 * Created by You on November 20, 2012.
 * Copyright 2012, Your Company All rights reserved.
 */

@import <Foundation/CPObject.j>
@import <AppKit/AppKit.j>
@import "Project.j"
@import "UserPreferencesController.j"
@import "ServerAdminController.j"
@import "WorkflowController.j"
@import "ProjectController.j"
// @import "RodanAPIController.j"


@implementation AppController : CPObject
{
    @outlet     CPWindow    theWindow;  //this "outlet" is connected automatically by the Cib
    @outlet     CPMenu      theMenu;
    @outlet     CPToolbar   theToolbar;

    @outlet     CPTextField username;
    @outlet     CPTextField password;
    @outlet     CPView      projectStatusView;
    @outlet     CPView      loginScreenView;
    @outlet     CPView      selectProjectView;
    @outlet     CPView      manageWorkflowsView;
    @outlet     CPView      interactiveJobsView;
    @outlet     CPView      manageImagesView;
    @outlet     CPView      usersGroupsView;
                CPView      contentView;

    @outlet     CPScrollView    contentScrollView;


    @outlet     CPWindow    userPreferencesWindow;
    @outlet     CPView      accountPreferencesView;

    @outlet     CPWindow    serverAdminWindow;
    @outlet     CPView      userAdminView;

    @outlet     CPWindow    newProjectWindow;
    @outlet     CPWindow    openProjectWindow;

    @outlet     CPWindow    newWorkflowWindow;


    CGRect      _theWindowBounds;

}

- (id)awakeFromCib
{
    CPLogRegister(CPLogConsole);
    CPLog("awakeFromCib");

    [theWindow setFullPlatformWindow:YES];
    [theMenu setMenuBarVisible:NO];

    var contentView = [theWindow contentView];
    _theWindowBounds = [contentView bounds];

    [theToolbar setVisible:NO];

    [contentScrollView initWithFrame:CGRectMake(0, 0, CGRectGetWidth(_theWindowBounds), CGRectGetHeight(_theWindowBounds) + 60)];
    [contentScrollView setAutoresizingMask:CPViewHeightSizable ];
    [contentScrollView setHasHorizontalScroller:YES];
    [contentScrollView setHasVerticalScroller:YES];
    [contentScrollView setAutohidesScrollers:YES];
    [contentScrollView setAutoresizesSubviews:YES];

    // [loginScreenView setBounds:CGRectMake(0, 0, CGRectGetWidth(_theWindowBounds), CGRectGetHeight(_theWindowBounds))];

    [contentScrollView setDocumentView:loginScreenView];
    [contentView setSubviews:[contentScrollView]];
}


- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    CPLog("Application Did Finish Launching");
}

- (IBAction)didLogIn:(id)aSender
{
    CPLog("User wants to log in.");
    CPLog("The Value of the Username: " + [username stringValue]);
    CPLog("The Value of the Password: " + [password stringValue]);

    // [projectStatusView setAutoresizingMask:CPViewWidthSizable];
    // [CPMenu setMenuBarVisible:YES];
    [contentScrollView setDocumentView:selectProjectView];
    // [contentScrollView setNeedsDisplay];
}

- (IBAction)switchWorkspace:(id)aSender
{
    CPLog("switchWorkspace called");
    console.log([contentScrollView subviews]);
    switch ([aSender itemIdentifier])
    {
        case @"statusToolbarButton":
            CPLog("Status Button!");
            [contentScrollView setDocumentView:projectStatusView];
            break;
        case @"manageImagesToolbarButton":
            CPLog("Manage Images!");
            [contentScrollView setDocumentView:manageImagesView];
            break;
        case @"manageWorkflowsToolbarButton":
            CPLog("Manage Workflows!");
            [contentScrollView setDocumentView:manageWorkflowsView];
            break;
        case @"interactiveJobsToolbarButton":
            CPLog("Interactive Jobs!");
            [contentScrollView setDocumentView:interactiveJobsView];
            break;
        case @"usersGroupsToolbarButton":
            CPLog("Users and Groups!");
            [contentScrollView setDocumentView:usersGroupsView];
            break;
        default:
            console.log("Unknown identifier");
            break;z
    }
}

- (IBAction)didOpenProject:(id)aSender
{
    [theWindow setTitle:@"Rodan — My Amazing Project"];
    [theToolbar setVisible:YES];
    [contentScrollView setDocumentView:projectStatusView];
}

- (IBAction)openUserPreferences:(id)aSender
{
    [userPreferencesWindow center];
    var preferencesContentView = [userPreferencesWindow contentView];
    [preferencesContentView addSubview:accountPreferencesView];
    [userPreferencesWindow orderFront:aSender];
}

- (IBAction)openServerAdmin:(id)aSender
{
    [serverAdminWindow center];
    var serverAdminContentView = [serverAdminWindow contentView];
    [serverAdminContentView addSubview:userAdminView];
    [serverAdminWindow orderFront:aSender];
}

- (IBAction)newProject:(id)aSender
{
    [newProjectWindow center];
    [newProjectWindow orderFront:aSender];
}

- (IBAction)openProject:(id)aSender
{
    [openProjectWindow center];
    [openProjectWindow orderFront:aSender];
}

- (IBAction)closeProject:(id)aSender
{
    CPLog("Close Project");
    var alert = [[CPAlert alloc] init];
    [alert setTitle:"Informational Alert"];
    [alert setMessageText:"Informational Alert"];
    [alert setInformativeText:"CPAlerts can also be used as sheets! With the same options as before."];
    [alert setShowsHelp:YES];
    [alert setShowsSuppressionButton:YES];
    [alert setAlertStyle:CPInformationalAlertStyle];
    [alert addButtonWithTitle:"Okay"];

    var closeProjectController = [[SheetController alloc] init];
    [alert setDelegate:closeProjectController];
    [closeProjectController setSheet:alert];
    [closeProjectController beginSheet]
}

- (IBAction)newWorkflow:(id)aSender
{
    [newWorkflowWindow center];
    [newWorkflowWindow orderFront:aSender];
}

@end


@implementation SheetController : CPObject
{
    CPAlert sheet @accessors;
}

- (void)beginSheet
{
    CPLog("Beginning Sheet");
    [sheet beginSheetModalForWindow:[CPApp mainWindow]];
}

- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    CPLog("Alert did End returning " + returnCode);
}
@end


