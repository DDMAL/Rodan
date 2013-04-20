@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "../Models/Project.j"
@import "../Transformers/ArrayCountTransformer.j"

@global RodanShouldLoadProjectNotification
@global RodanDidLoadProjectsNotification
@global RodanDidLoadProjectNotification
@global RodanDidCloseProjectNotification

@global activeUser
@global activeProject

@implementation ProjectController : CPObject
{
    @outlet     CPArrayController           projectArrayController;
                CPValueTransformer          projectCountTransformer;
    @outlet     LoadActiveProjectDelegate   activeProjectDelegate;
    @outlet     CPButtonBar                 projectAddRemoveButtonBar;
    @outlet     CPView                      selectProjectView;

    @outlet     PageController              pageController;
    @outlet     CPArrayController           pageArrayController;
    @outlet     WorkflowController          workflowController;
    @outlet     CPArrayController           workflowArrayController;
    @outlet     JobController               jobController;
}

- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (id)awakeFromCib
{
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(shouldLoadProject:)
                                          name:RodanShouldLoadProjectNotification
                                          object:nil];

    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(showProjectsChooser:)
                                          name:RodanDidLoadProjectsNotification
                                          object:nil];

    var backgroundTexture = [[CPImage alloc] initWithContentsOfFile:[[CPBundle mainBundle] pathForResource:@"workflow-backgroundTexture.png"]
                                             size:CGSizeMake(200.0, 200.0)];

    [selectProjectView setBackgroundColor:[CPColor colorWithPatternImage:backgroundTexture]];
}

- (CPString)remoteActionContentType:(WLRemoteAction)anAction
{
    return @"application/json; charset=utf-8";
}

- (void)fetchProjects
{
    [WLRemoteAction schedule:WLRemoteActionGetType path:"/projects/" delegate:self message:"Loading projects"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    var p = [MinimalProject objectsFromJson:[anAction result].results];
    [projectArrayController addObjects:p];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadProjectsNotification
                                          object:nil];
}

- (@action)newProject:(id)aSender
{
    var newProject = [[MinimalProject alloc] initWithCreator:[activeUser pk]];
    [projectArrayController addObject:newProject];
    [newProject ensureCreated];
}

- (@action)shouldDeleteProjects:(id)aSender
{
    // get selected projects
    var numToBeDeleted = [[projectArrayController selectedObjects] count];
    if (numToBeDeleted > 1)
    {
        var plThis = "These",
            plProj = "projects";
    }
    else
    {
        var plThis = "This",
            plProj = "project";
    }

    var message = [CPString stringWithFormat:@"%@ %@ %@ and all associated files will be deleted! This cannot be undone. Are you sure?", plThis, numToBeDeleted, plProj];
    // pop up a warning
    alert = [[CPAlert alloc] init];
    [alert setMessageText:message];
    [alert setDelegate:self];
    [alert setAlertStyle:CPCriticalAlertStyle];
    [alert addButtonWithTitle:@"Delete"];
    [alert addButtonWithTitle:@"Cancel"];
    [alert runModal];
}

- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    if (returnCode == 0)
        [self deleteProjects];
}

- (void)deleteProjects
{
    var selectedObjects = [projectArrayController selectedObjects];
    [projectArrayController removeObjects:selectedObjects];
    [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
}

- (void)shouldLoadProject:(CPNotification)aNotification
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[[aNotification object] pk]
                    delegate:activeProjectDelegate
                    message:"Loading Project"];
}

- (IBAction)openProject:(id)aSender
{
    var selectedProject = [[projectArrayController selectedObjects] objectAtIndex:0];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadProjectNotification
                                          object:selectedProject];

}

- (void)emptyProjectArrayController
{
    [[projectArrayController contentArray] removeAllObjects];
}

#pragma mark -
#pragma mark Project Opening and Closing

- (void)showProjectsChooser:(id)aNotification
{
    var addButton = [CPButtonBar plusPopupButton],
        removeButton = [CPButtonBar minusButton],
        addProjectTitle = @"Add Project...";

    [addButton addItemsWithTitles:[addProjectTitle]];
    [projectAddRemoveButtonBar setButtons:[addButton, removeButton]];

    var addProjectItem = [addButton itemWithTitle:addProjectTitle];

    [addProjectItem setAction:@selector(newProject:)];
    [addProjectItem setTarget:self];

    [removeButton setAction:@selector(shouldDeleteProjects:)];
    [removeButton setTarget:self];

    [removeButton bind:@"enabled"
                  toObject:projectArrayController
                  withKeyPath:@"selectedObjects.@count"
                  options:nil]

    [selectProjectView setFrame:[[[CPApp delegate] contentScrollView] bounds]];
    [selectProjectView setAutoresizingMask:CPViewWidthSizable];
    [[[CPApp delegate] contentScrollView] setDocumentView:selectProjectView];
}

- (void)didCloseProject:(CPNotification)aNotification
{
    // perform some cleanup
    [self emptyProjectArrayController];
    [pageController emptyPageArrayController];
    [workflowController emptyWorkflowArrayController];

    [[[CPApp delegate] theToolbar] setVisible:NO];
    [CPMenu setMenuBarVisible:NO];

    // this should fire off a request to reload the projects and then show the
    // project chooser once they have returned.
    [self fetchProjects];
    [jobController fetchJobs]
}

- (IBAction)closeProject:(id)aSender
{
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidCloseProjectNotification
                                          object:nil];
}

@end

@implementation LoadActiveProjectDelegate : CPObject
{
    @outlet     CPArrayController       pageArrayController;
    @outlet     CPArrayController       workflowArrayController;
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [WLRemoteObject setDirtProof:YES];
    activeProject = [[Project alloc] initWithJson:[anAction result]];
    [WLRemoteObject setDirtProof:NO];

    [pageArrayController bind:@"contentArray"
                         toObject:activeProject
                         withKeyPath:@"pages"
                         options:nil];

    [workflowArrayController bind:@"contentArray"
                             toObject:activeProject
                             withKeyPath:@"workflows"
                             options:nil];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadProjectNotification
                                          object:nil];

}

@end
