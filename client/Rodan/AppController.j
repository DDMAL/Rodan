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
@import <TNKit/TNKit.j>

@import "Categories/CPButtonBar+PopupButtons.j"
@import "Categories/CPArrayController+selectedObject.j"

@import "Transformers/ArrayCountTransformer.j"
@import "Transformers/GameraClassNameTransformer.j"
@import "Transformers/CheckBoxTransformer.j"
@import "Transformers/UsernameTransformer.j"
@import "Transformers/ImageSizeTransformer.j"
@import "Transformers/DateFormatTransformer.j"

@import "Controllers/LogInController.j"
@import "Controllers/UserPreferencesController.j"
@import "Controllers/ServerAdminController.j"
@import "Controllers/WorkflowController.j"
@import "Controllers/WorkflowDesignerController.j"
@import "Controllers/ProjectController.j"
@import "Controllers/PageController.j"
@import "Controllers/JobController.j"
@import "Models/Project.j"

RodanDidLoadProjectNotification = @"RodanDidLoadProjectNotification";
RodanDidCloseProjectNotification = @"RodanDidCloseProjectNotification";
RodanShouldLoadProjectNotification = @"RodanShouldLoadProjectNotification";
RodanDidLoadProjectsNotification = @"RodanDidLoadProjectsNotification";

RodanDidLoadJobsNotification = @"RodanDidLoadJobsNotification";
RodanJobTreeNeedsRefresh = @"RodanJobTreeNeedsRefresh";

RodanDidLoadWorkflowsNotification = @"RodanDidLoadWorkflowsNotification";
RodanDidLoadWorkflowNotification = @"RodanDidLoadWorkflowNotification";
RodanShouldLoadWorkflowDesignerNotification = @"RodanShouldLoadWorkflowDesignerNotification";

RodanRemoveJobFromWorkflowNotification = @"RodanRemoveJobFromWorkflowNotification";
RodanWorkflowTreeNeedsRefresh = @"RodanWorkflowTreeNeedsRefresh";

RodanMustLogInNotification = @"RodanMustLogInNotification";
RodanDidLogInNotification = @"RodanDidLogInNotification";
RodanCannotLogInNotification = @"RodanCannotLogInNotification";
RodanLogInErrorNotification = @"RodanLogInErrorNotification";
RodanDidLogOutNotification = @"RodanDidLogOutNotification";

isLoggedIn = NO;
activeUser = nil;     // URI to the currently logged-in user
activeProject = nil;  // URI to the currently open project

@implementation AppController : CPObject
{
    @outlet     CPWindow    theWindow;
    @outlet     TNToolbar   theToolbar  @accessors(readonly);
                CPBundle    theBundle;

    @outlet     CPView      projectStatusView;
    @outlet     CPView      loginWaitScreenView;
    @outlet     CPView      manageWorkflowsView;
    @outlet     CPView      interactiveJobsView;
    @outlet     CPView      managePagesView;
    @outlet     CPView      usersGroupsView;
    @outlet     CPView      chooseWorkflowView;
    @outlet     CPView      workflowDesignerView;
                CPView      contentView;

    // @outlet     CPScrollView    contentScrollView;
                CPScrollView        contentScrollView       @accessors(readonly);
    @outlet     CPArrayController   projectArrayController;

    @outlet     CPWindow    userPreferencesWindow;
    @outlet     CPView      accountPreferencesView;

    @outlet     CPWindow    serverAdminWindow;
    @outlet     CPView      userAdminView;

    @outlet     CPToolbarItem   statusToolbarItem;
    @outlet     CPToolbarItem   pagesToolbarItem;
    @outlet     CPToolbarItem   workflowsToolbarItem;
    @outlet     CPToolbarItem   jobsToolbarItem;
    @outlet     CPToolbarItem   usersToolbarItem;
    @outlet     CPToolbarItem   workflowDesignerToolbarItem;
    @outlet     CPButtonBar     workflowAddRemoveBar;

    @outlet     CPMenu          switchWorkspaceMenu;
    @outlet     CPMenuItem      rodanMenuItem;

    @outlet     ProjectController           projectController;
    @outlet     PageController              pageController;
    @outlet     JobController               jobController;
    @outlet     UploadButton                imageUploadButton;
    @outlet     LogInController             logInController;
    @outlet     WorkflowController          workflowController;
    @outlet     WorkflowDesignerController  workflowDesignerController;

    CGRect      _theWindowBounds;

                CPCookie        sessionID;
                CPCookie        CSRFToken;
                CPString        projectName;

}

+ (void)initialize
{
    [super initialize];
    [self registerValueTransformers];
}

+ (void)registerValueTransformers
{
    arrayCountTransformer = [[ArrayCountTransformer alloc] init];
    [ArrayCountTransformer setValueTransformer:arrayCountTransformer
                             forName:@"ArrayCountTransformer"];

    gameraClassNameTransformer = [[GameraClassNameTransformer alloc] init];
    [GameraClassNameTransformer setValueTransformer:gameraClassNameTransformer
                                forName:@"GameraClassNameTransformer"];

    usernameTransformer = [[UsernameTransformer alloc] init];
    [UsernameTransformer setValueTransformer:usernameTransformer
                                forName:@"UsernameTransformer"];

    imageSizeTransformer = [[ImageSizeTransformer alloc] init];
    [ImageSizeTransformer setValueTransformer:imageSizeTransformer
                                forName:@"ImageSizeTransformer"];

    dateFormatTransformer = [[DateFormatTransformer alloc] init];
    [DateFormatTransformer setValueTransformer:dateFormatTransformer
                                forName:@"DateFormatTransformer"];
}

- (id)awakeFromCib
{
    CPLogRegister(CPLogConsole);
    isLoggedIn = NO;

    [[LogInCheckController alloc] initCheckingStatus];

    sessionID = [[CPCookie alloc] initWithName:@"sessionid"];
    CSRFToken = [[CPCookie alloc] initWithName:@"csrftoken"];

    [[WLRemoteLink sharedRemoteLink] setDelegate:self];

    [theWindow setFullPlatformWindow:YES];

    [imageUploadButton setValue:[CSRFToken value] forParameter:@"csrfmiddlewaretoken"]
    [imageUploadButton setBordered:YES];
    [imageUploadButton setFileKey:@"files"];
    [imageUploadButton allowsMultipleFiles:YES];
    [imageUploadButton setDelegate:pageController];
    [imageUploadButton setURL:@"/pages/"];

    theBundle = [CPBundle mainBundle],
    contentView = [theWindow contentView],
    _theWindowBounds = [contentView bounds];
    var center = [CPNotificationCenter defaultCenter];

    // [center addObserver:self selector:@selector(didOpenProject:) name:RodanDidLoadProjectNotification object:nil];
    [center addObserver:self selector:@selector(didLoadProject:) name:RodanDidLoadProjectNotification object:nil];
    // [center addObserver:self selector:@selector(showProjectsChooser:) name:RodanDidLoadProjectsNotification object:nil];
    [center addObserver:self selector:@selector(didCloseProject:) name:RodanDidCloseProjectNotification object:nil];
    [center addObserver:self selector:@selector(showWorkflowDesigner:) name:RodanDidLoadWorkflowNotification object:nil];

    [center addObserver:self selector:@selector(didLogIn:) name:RodanDidLogInNotification object:nil];
    [center addObserver:self selector:@selector(mustLogIn:) name:RodanMustLogInNotification object:nil];
    [center addObserver:self selector:@selector(cannotLogIn:) name:RodanCannotLogInNotification object:nil];
    [center addObserver:self selector:@selector(cannotLogIn:) name:RodanLogInErrorNotification object:nil];
    [center addObserver:self selector:@selector(didLogOut:) name:RodanDidLogOutNotification object:nil];

    [theToolbar setVisible:NO];

    var statusToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-status.png"] size:CGSizeMake(32.0, 32.0)],
        pagesToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-images.png"] size:CGSizeMake(40.0, 32.0)],
        workflowsToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-workflows.png"] size:CGSizeMake(32.0, 32.0)],
        jobsToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-jobs.png"] size:CGSizeMake(32.0, 32.0)],
        usersToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-users.png"] size:CGSizeMake(46.0, 32.0)],
        workflowDesignerToolbarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"toolbar-workflow-designer.png"] size:CGSizeMake(32.0, 32.0)],
        backgroundTexture = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"workflow-backgroundTexture.png"] size:CGSizeMake(200.0, 200.0)];

    [statusToolbarItem setImage:statusToolbarIcon];
    [pagesToolbarItem setImage:pagesToolbarIcon];
    [workflowsToolbarItem setImage:workflowsToolbarIcon];
    [jobsToolbarItem setImage:jobsToolbarIcon];
    [usersToolbarItem setImage:usersToolbarIcon];
    [workflowDesignerToolbarItem setImage:workflowDesignerToolbarIcon];

    [chooseWorkflowView setBackgroundColor:[CPColor colorWithPatternImage:backgroundTexture]];

    [contentView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

    contentScrollView = [[CPScrollView alloc] initWithFrame:[contentView bounds]];
    [contentScrollView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];
    [contentScrollView setHasHorizontalScroller:YES];
    [contentScrollView setHasVerticalScroller:YES];
    [contentScrollView setAutohidesScrollers:YES];

    [contentView setSubviews:[contentScrollView]];
}


- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{

    window.onbeforeunload = function()
    {
        return "This will terminate the Application. Are you sure you want to leave?";
    }

    [CPMenu setMenuBarVisible:NO];
    var menubarIcon = [[CPImage alloc] initWithContentsOfFile:[theBundle pathForResource:@"menubar-icon.png"] size:CGSizeMake(16.0, 16.0)];
    [rodanMenuItem setImage:menubarIcon];

    [loginWaitScreenView setFrame:[contentScrollView bounds]];
    [loginWaitScreenView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:loginWaitScreenView];
}

- (void)mustLogIn:(id)aNotification
{
    var blankView = [[CPView alloc] init];
    [contentScrollView setDocumentView:blankView];
    [logInController runLogInSheet];
}

- (void)cannotLogIn:(id)aNotification
{
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
    var authResponse = [aNotification object];

    isLoggedIn = YES;
    activeUser = [authResponse valueForKey:@"user"];

    [projectController fetchProjects];
    [jobController fetchJobs];
}

- (void)didLogOut:(id)aNotification
{
    [projectController emptyProjectArrayController];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanMustLogInNotification
                                          object:nil];
}

- (IBAction)logOut:(id)aSender
{
    [LogOutController logOut];
}

- (void)didLoadProject:(CPNotification)aNotification
{
    [theWindow setTitle:@"Rodan — " + [activeProject projectName]];

    [CPMenu setMenuBarVisible:YES];
    [theToolbar setVisible:YES];

    [projectStatusView setFrame:[contentScrollView bounds]];
    [projectStatusView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:projectStatusView];
}


#pragma mark -
#pragma mark Switch Workspaces

- (IBAction)switchWorkspaceToProjectStatus:(id)aSender
{
    [projectStatusView setFrame:[contentScrollView bounds]];
    [projectStatusView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:projectStatusView];
}

- (IBAction)switchWorkspaceToManagePages:(id)aSender
{
    [managePagesView setFrame:[contentScrollView bounds]];
    [managePagesView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:managePagesView];
}

- (IBAction)switchWorkspaceToManageWorkflows:(id)aSender
{
    [manageWorkflowsView setFrame:[contentScrollView bounds]];
    [manageWorkflowsView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:manageWorkflowsView];
}

- (IBAction)switchWorkspaceToInteractiveJobs:(id)aSender
{
    [interactiveJobsView setFrame:[contentScrollView bounds]];
    [interactiveJobsView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:interactiveJobsView];
}

- (IBAction)switchWorkspaceToUsersGroups:(id)aSender
{
    [usersGroupsView setFrame:[contentScrollView bounds]];
    [usersGroupsView setAutoresizingMask:CPViewWidthSizable];
    [contentScrollView setDocumentView:usersGroupsView];
}

- (IBAction)switchWorkspaceToWorkflowDesigner:(id)aSender
{
    [chooseWorkflowView setFrame:[contentScrollView bounds]];
    [chooseWorkflowView layoutIfNeeded];
    [contentScrollView setDocumentView:chooseWorkflowView];
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

- (IBAction)showWorkflowDesigner:(id)aSender
{
    [workflowDesignerView setFrame:[contentScrollView bounds]];
    [workflowDesignerView layoutIfNeeded];
    [contentScrollView setDocumentView:workflowDesignerView];
}

- (void)observerDebug:(id)aNotification
{
    CPLog("Notification was Posted: " + [aNotification name]);
}

#pragma mark WLRemoteLink Delegate

- (void)remoteLink:(WLRemoteLink)aLink willSendRequest:(CPURLRequest)aRequest withDelegate:(id)aDelegate context:(id)aContext
{
    switch ([[aRequest HTTPMethod] uppercaseString])
    {
        case "POST":
        case "PUT":
        case "PATCH":
        case "DELETE":
            [aRequest setValue:[CSRFToken value] forHTTPHeaderField:"X-CSRFToken"];
    }
}
@end
