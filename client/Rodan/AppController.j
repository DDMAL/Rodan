/*
 * AppController.j
 * Rodan
 *
 * Created by You on November 20, 2012.
 * Copyright 2012, Your Company All rights reserved.
 */

@import <Foundation/CPObject.j>
@import <AppKit/AppKit.j>
@import <FileUpload/FileUpload.j>
@import <Ratatosk/Ratatosk.j>

@import "Controller/LogInController.j"
@import "Controller/UserPreferencesController.j"
@import "Controller/ServerAdminController.j"
@import "Controller/WorkflowController.j"
@import "Controller/ProjectController.j"
@import "Controller/PageController.j"
@import "Model/Project.j"

RodanDidOpenProjectNotification = @"RodanDidOpenProjectNotification";
RodanDidLoadProjectsNotification = @"RodanDidLoadProjectsNotification";

RodanMustLogInNotification = @"RodanMustLogInNotification";
RodanDidLogInNotification = @"RodanDidLogInNotification";
RodanCannotLogInNotification = @"RodanCannotLogInNotification";
RodanLogInErrorNotification = @"RodanLogInErrorNotification";
RodanDidLogOutNotification = @"RodanDidLogOutNotification";

isLoggedIn = NO;
activeUser = "";     // URI to the currently logged-in user
activeProject = "";  // URI to the currently open project

@implementation AppController : CPObject
{
    @outlet     CPWindow    theWindow;  //this "outlet" is connected automatically by the Cib
    @outlet     CPMenu      theMenu;
    @outlet     CPToolbar   theToolbar;
                CPBundle    theBundle;

    @outlet     CPView      projectStatusView;
    @outlet     CPView      loginScreenView;
    @outlet     CPView      loginWaitScreenView;
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

    @outlet     CPToolbarItem   statusToolbarItem;
    @outlet     CPToolbarItem   pagesToolbarItem;
    @outlet     CPToolbarItem   workflowsToolbarItem;
    @outlet     CPToolbarItem   jobsToolbarItem;
    @outlet     CPToolbarItem   usersToolbarItem;

    @outlet     ProjectController   projectController;
    @outlet     PageController      pageController;
    @outlet     UploadButton        imageUploadButton;

    CGRect      _theWindowBounds;

                CPCookie        sessionID;
                CPCookie        CSRFToken;

}

- (id)awakeFromCib
{
    CPLogRegister(CPLogConsole);
    CPLog("AppController Awake From CIB");
    isLoggedIn = NO;

    [[LogInCheckController alloc] initCheckingStatus];

    var sessionID = [[CPCookie alloc] initWithName:@"sessionid"],
        CSRFToken = [[CPCookie alloc] initWithName:@"csrftoken"];
    [WLRemoteLink addValue:[CSRFToken value] forGlobalHeaderField:@"X-CSRFToken"];

    [theWindow setFullPlatformWindow:YES];

    [imageUploadButton setBordered:YES];
    [imageUploadButton allowsMultipleFiles:YES];
    [imageUploadButton setDelegate:pageController];
    [imageUploadButton setURL:@"/pages/"];

    theBundle = [CPBundle mainBundle],
    contentView = [theWindow contentView],
    _theWindowBounds = [contentView bounds],
    center = [CPNotificationCenter defaultCenter];

    [center addObserver:self selector:@selector(didOpenProject:) name:RodanDidOpenProjectNotification object:nil];
    [center addObserver:self selector:@selector(showProjectsChooser:) name:RodanDidLoadProjectsNotification object:nil];

    [center addObserver:self selector:@selector(didLogIn:) name:RodanDidLogInNotification object:nil];
    [center addObserver:self selector:@selector(mustLogIn:) name:RodanMustLogInNotification object:nil];
    [center addObserver:self selector:@selector(cannotLogIn:) name:RodanCannotLogInNotification object:nil];
    [center addObserver:self selector:@selector(cannotLogIn:) name:RodanLogInErrorNotification object:nil];
    [center addObserver:self selector:@selector(didLogOut:) name:RodanDidLogOutNotification object:nil];

    /* Debugging Observers */
    [center addObserver:self selector:@selector(observerDebug:) name:RodanDidOpenProjectNotification object:nil];
    [center addObserver:self selector:@selector(observerDebug:) name:RodanDidLoadProjectsNotification object:nil];
    /* ------------------- */

    [theToolbar setVisible:NO];

    var statusToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-status.png"] size:CGSizeMake(32.0, 32.0)],
        statusToolbarIconSelected = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-status-selected.png"] size:CGSizeMake(32.0, 32.0)],
        pagesToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-images.png"] size:CGSizeMake(40.0, 32.0)],
        pagesToolbarIconSelected = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-images-selected.png"] size:CGSizeMake(40.0, 32.0)],
        workflowsToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-workflows.png"] size:CGSizeMake(32.0, 32.0)],
        workflowsToolbarIconSelected = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-workflows-selected.png"] size:CGSizeMake(32.0, 32.0)],
        jobsToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-jobs.png"] size:CGSizeMake(32.0, 32.0)],
        jobsToolbarIconSelected = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-jobs-selected.png"] size:CGSizeMake(32.0, 32.0)],
        usersToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-users.png"] size:CGSizeMake(46.0, 32.0)],
        usersToolbarIconSelected = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-users-selected.png"] size:CGSizeMake(46.0, 32.0)];

    [statusToolbarItem setImage:statusToolbarIcon];
    [statusToolbarItem setAlternateImage:statusToolbarIconSelected];
    [pagesToolbarItem setImage:pagesToolbarIcon];
    [pagesToolbarItem setAlternateImage:pagesToolbarIconSelected];
    [workflowsToolbarItem setImage:workflowsToolbarIcon];
    [workflowsToolbarItem setAlternateImage:workflowsToolbarIconSelected];
    [jobsToolbarItem setImage:jobsToolbarIcon];
    [jobsToolbarItem setAlternateImage:jobsToolbarIconSelected];
    [usersToolbarItem setImage:usersToolbarIcon];
    [usersToolbarItem setAlternateImage:usersToolbarIconSelected];

    [contentScrollView initWithFrame:CGRectMake(0, 0, CGRectGetWidth(_theWindowBounds), CGRectGetHeight(_theWindowBounds) + 60)];
    [contentScrollView setAutoresizingMask:CPViewHeightSizable ];
    [contentScrollView setHasHorizontalScroller:YES];
    [contentScrollView setHasVerticalScroller:YES];
    [contentScrollView setAutohidesScrollers:YES];
    [contentScrollView setAutoresizesSubviews:YES];

    [contentView setSubviews:[contentScrollView]];
}


- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    CPLog("Application Did Finish Launching");
    [contentScrollView setDocumentView:loginWaitScreenView];
}

- (void)mustLogIn:(id)aNotification
{
    // show log in screen
    [contentScrollView setDocumentView:loginScreenView];
}

- (void)cannotLogIn:(id)aNotification
{
    CPLog("Cannot log in called");
    isLoggedIn = NO;
    // display an alert that they cannot log in
    var alert = [[CPAlert alloc] init];
    [alert setTitle:@"Cannot Log In"];
    [alert setMessageText:@"You cannot log in"];
    [alert setInformativeText:@"Please check your username and password. If you are still having difficulties, please contact an administrator."];
    [alert setShowsHelp:YES];
    [alert setAlertStyle:CPInformationalAlertStyle];
    [alert addButtonWithTitle:"Ok"];
    [alert runModal];
}

- (void)didLogIn:(id)aNotification
{
    CPLog("Did Log In Successfully.");
    authResponse = [aNotification object];

    isLoggedIn = YES;
    activeUser = [authResponse valueForKey:@"user"];

    [projectController fetchProjects];
}

- (void)didLogOut:(id)aNotification
{
    [contentScrollView setDocumentView:loginScreenView];
}

- (void)showProjectsChooser:(id)aNotification
{
    [contentScrollView setDocumentView:selectProjectView];
}

- (IBAction)logOut:(id)aSender
{
    [LogOutController logOut];
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
            break;
    }
}

- (void)didOpenProject:(CPNotification)aNotification
{
    activeProject = [[aNotification object] resourceURI];
    projectName = [[aNotification object] projectName];
    [theWindow setTitle:@"Rodan — " + projectName];
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

- (void)observerDebug:(id)aNotification
{
    CPLog("Notification was Posted: " + [aNotification name]);
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


