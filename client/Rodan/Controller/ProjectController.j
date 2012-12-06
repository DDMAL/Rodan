@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "RodanAPIController.j"
@import "../Model/Project.j"

@implementation ProjectController : CPObject
{
    @outlet     CPTableView         projectChooseTable;
    @outlet     CPArrayController   projectArrayController;
    @outlet     CPWindow            createProjectWindow;

    @outlet     CPTextField         newProjectName;
    @outlet     CPTextField         newProjectDescription;
}

- (id)init
{
    if (self = [super init])
    {
        CPLog("Project controller init");
    }
    return self;
}

- (id)awakeFromCib
{
    // [Project fetchProjects];
    CPLog("Awake from CIB Project Controller");
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
    console.log("anAction");
    // console.log([anAction result].objects);
    p = [Project objectsFromJson:[anAction result].results];
    [projectArrayController addObjects:p];
}

- (IBAction)openAddProjectWindow:(id)aSender
{
    // pop up window
    [createProjectWindow center];
    [createProjectWindow makeKeyAndOrderFront:aSender];
}

- (IBAction)createNewProject:(id)aSender
{
    [createProjectWindow close];

    // get window username & description
    projectName = [newProjectName objectValue];
    projectDescription = [newProjectDescription objectValue];

    [newProjectName setObjectValue:@""];
    [newProjectDescription setObjectValue:@""];

    // add to JSON description
    newProjectObject = {
        'name': projectName,
        'description': projectDescription,
        'creator': "/api/v1/user/1/",
        'resource_uri': nil
    };

    // create object
    p = [[Project alloc] initWithJson:newProjectObject];
    [projectArrayController addObject:p];
    [p ensureCreated];
}

- (IBAction)deleteProject:(id)aSender
{
    // get selected projects
    numToBeDeleted = [[projectArrayController selectedObjects] count];
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

    message = [CPString stringWithFormat:@"%@ %@ %@ will be deleted! This cannot be undone.", plThis, numToBeDeleted, plProj];
    // pop up a warning
    alert = [[CPAlert alloc] init];
    [alert setMessageText:message];
    [alert setDelegate:self];
    [alert setAlertStyle:CPCriticalAlertStyle];
    [alert addButtonWithTitle:@"Delete"];
    [alert addButtonWithTitle:@"Cancel"];
    [alert runModal];
    // delete project
}

- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    CPLog("The alert ended with a response of " + returnCode);
    console.log(theAlert);
    if (returnCode == 0)
    {
        // delete
        console.log("Deleting");
        selectedObjects = [projectArrayController selectedObjects];
        [projectArrayController removeObjects:selectedObjects];

        for (var i = 0; i < selectedObjects.length; i++)
        {
            [selectedObjects[i] ensureDeleted];
        };
    }
}

- (IBAction)openProject:(id)aSender
{
    selectedObjects = [projectArrayController selectedObjects];
    if (selectedObjects > 1)
    {
        alert = [[CPAlert alloc] init];
        [alert setMessageText:@"You must choose just one project to open."];
        [alert setAlertStyle:CPWarningAlertStyle];
        [alert addButtonWithTitle:@"OK"];
        [alert runModal];
        return nil;
    }
    theProject = [selectedObjects objectAtIndex:0];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidOpenProjectNotification object:theProject];

}

@end
