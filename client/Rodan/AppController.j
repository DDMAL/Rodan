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


@implementation AppController : CPObject
{
    @outlet     CPWindow    theWindow;  //this "outlet" is connected automatically by the Cib

    @outlet     CPTextField username;
    @outlet     CPTextField password;
    @outlet     CPView      projectStatusView;
    @outlet     CPView      loginScreenView;
    @outlet     CPView      selectProjectView;
    @outlet     CPView      manageWorkflowsView;
    @outlet     CPView      interactiveJobsView;
    @outlet     CPView      manageImagesView;
                CPView      contentView;

    @outlet     CPScrollView    contentScrollView;
    @outlet     CPToolbar   theToolbar;

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

    var contentView = [theWindow contentView];
    _theWindowBounds = [contentView bounds];

    [theToolbar setVisible:NO];

    console.log(CGRectGetWidth(_theWindowBounds));

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
        // contentScrollView = [[CPScrollView alloc] initWithFrame:CGRectMake(0.0, 0.0, CGRectGetWidth([contentView bounds]), CGRectGetHeight([contentView bounds]))];
    // [theWindow setFullPlatformWindow:YES];
}

- (IBAction)didLogIn:(id)aSender
{
    CPLog("User wants to log in.");
    CPLog("The Value of the Username: " + [username stringValue]);
    CPLog("The Value of the Password: " + [password stringValue]);

    // [projectStatusView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:selectProjectView];
    // [contentScrollView setNeedsDisplay];
}

- (IBAction)switchWorkspace:(id)aSender
{
    // temporary place for enabling the toolbar
    if (![theToolbar isVisible])
    {
        [didOpenProject]
    }
    CPLog("switchWorkspace called");
    console.log(aSender);
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

- (IBAction)newWorkflow:(id)aSender
{
    [newWorkflowWindow center];
    [newWorkflowWindow orderFront:aSender];
}

@end
