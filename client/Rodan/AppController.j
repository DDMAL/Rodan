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


@implementation AppController : CPObject
{
    @outlet     CPWindow    theWindow;  //this "outlet" is connected automatically by the Cib
    @outlet     CPWindow    userPreferencesWindow;

    @outlet     CPTextField username;
    @outlet     CPTextField password;
    @outlet     CPView      projectStatusView;
    @outlet     CPView      loginScreenView;
    @outlet     CPView      manageWorkflowsView;
    @outlet     CPView      interactiveJobsView;
    @outlet     CPView      manageImagesView;
                CPView      contentView;

    @outlet     CPScrollView    contentScrollView;
    @outlet     CPToolbar   theToolbar;
}

- (id)awakeFromCib
{
    CPLogRegister(CPLogConsole);
    CPLog("awakeFromCib");

    var contentView = [theWindow contentView],
        bounds = [contentView bounds],
        windowSize = [[theWindow platformWindow] contentBounds];

    [theToolbar setVisible:NO];

    [contentScrollView initWithFrame:CGRectMake(0,0, CGRectGetWidth(windowSize), CGRectGetHeight(windowSize))];
    [contentScrollView setHasHorizontalScroller:YES];
    [contentScrollView setHasVerticalScroller:YES];
    [contentScrollView setAutohidesScrollers:YES];
    [contentScrollView setAutoresizesSubviews:YES];

    [contentScrollView addSubview:loginScreenView];
    [contentView addSubview:contentScrollView];
}


- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    CPLog("Application Did Finish Launching");
        // contentScrollView = [[CPScrollView alloc] initWithFrame:CGRectMake(0.0, 0.0, CGRectGetWidth([contentView bounds]), CGRectGetHeight([contentView bounds]))];
    [theWindow setFullPlatformWindow:YES];
}

- (IBAction)didLogIn:(id)aSender
{
    CPLog("User wants to log in.");
    CPLog("The Value of the Username: " + [username stringValue]);
    CPLog("The Value of the Password: " + [password stringValue]);

    [contentScrollView replaceSubview:loginScreenView with:projectStatusView];
    [theToolbar setVisible:YES];
}

- (IBAction)switchWorkspace:(id)aSender
{
    CPLog("switchWorkspace called");
    switch ([aSender itemIdentifier])
    {
        case @"statusToolbarButton":
            CPLog("Status Button!");
            [contentScrollView setSubviews:[projectStatusView]];
            break;
        case @"manageImagesToolbarButton":
            CPLog("Manage Images!");
            [contentScrollView setSubviews:[manageImagesView]];
            break;
        case @"manageWorkflowsToolbarButton":
            CPLog("Manage Workflows!");
            [contentScrollView setSubviews:[manageWorkflowsView]];
            break;
        case @"interactiveJobsToolbarButton":
            CPLog("Interactive Jobs!");
            [contentScrollView setSubviews:[interactiveJobsView]];
            break;
    }
}

- (IBAction)openUserPreferences:(id)aSender
{
    var prefsController = [[UserPreferencesController alloc] init];
    [[prefsController window] orderFront:self];
    // [userPreferencesWindow center];
    // [userPreferencesWindow makeKeyAndOrderFront:aSender];
}
@end
