@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "../Models/Project.j"
@import "../Transformers/ArrayCountTransformer.j"

@global RodanDidLoadProjectsNotification
@global RodanDidOpenProjectNotification
@global activeUser

@implementation ProjectController : CPObject
{
    @outlet     CPArrayController   projectArrayController;
    @outlet     CPWindow            createProjectWindow;
    @outlet     CPButton            createProjectButton;

    @outlet     CPTextField         newProjectName;
    @outlet     CPTextField         newProjectDescription;

                CPValueTransformer  projectCountTransformer;
}

- (id)init
{
    if (self = [super init])
    {
        // CPLog("Project controller init");
    }
    return self;
}

- (id)awakeFromCib
{
    // CPLog("Awake from CIB Project Controller");
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
    var p = [Project objectsFromJson:[anAction result].results];
    [projectArrayController addObjects:p];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadProjectsNotification
                                          object:nil];
}

- (@action)newProject:(id)aSender
{
    var newProject = [[Project alloc] initWithCreator:activeUser];
    [projectArrayController addObject:newProject];
    [newProject ensureCreated];
}

- (@action)deleteProject:(id)aSender
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

- (IBAction)openProject:(id)aSender
{
    var selectedObjects = [projectArrayController selectedObjects];
    if (selectedObjects > 1)
    {
        alert = [[CPAlert alloc] init];
        [alert setMessageText:@"You must choose just one project to open."];
        [alert setAlertStyle:CPWarningAlertStyle];
        [alert addButtonWithTitle:@"OK"];
        [alert runModal];
        return nil;
    }
    var theProject = [selectedObjects objectAtIndex:0];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidOpenProjectNotification
                                          object:theProject];

}

- (void)emptyProjectArrayController
{
    [[projectArrayController contentArray] removeAllObjects];
}

@end
