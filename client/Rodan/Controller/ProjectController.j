@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "../Model/Project.j"

@implementation ProjectController : CPObject
{
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
    CPLog("Remote Action did Finish");

    p = [Project objectsFromJson:[anAction result].results];
    [projectArrayController addObjects:p];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadProjectsNotification
                                          object:nil];
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

    /*
        Reset the text fields so that subsequent calls to the window
        do not maintain their former values
    */
    [newProjectName setObjectValue:@""];
    [newProjectDescription setObjectValue:@""];

    // add to JSON description
    newProjectObject = {
        'name': projectName,
        'description': projectDescription,
        'creator': activeUser,
    };

    // create object
    p = [[Project alloc] initWithJson:newProjectObject];

    [projectArrayController addObject:p];

    [p ensureCreated];
}

- (IBAction)selectDeleteProject:(id)aSender
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
}

- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    CPLog("The alert ended with a response of " + returnCode);
    if (returnCode == 0)
    {
        // delete
        console.log("Deleting");
        [self deleteProjects];
    }
}

- (void)deleteProjects
{
        selectedObjects = [projectArrayController selectedObjects];
        [projectArrayController removeObjects:selectedObjects];

        for (var i = 0; i < selectedObjects.length; i++)
        {
            [selectedObjects[i] ensureDeleted];
        };
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

// this tell the table how many rows it has…
- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    CPLog("Num Rows " + [projectList count]);
    return [projectList count];
}

// this defines what text will display for each row, in each column, for each table view.
- (id)tableView:(CPTableView)aTableView objectValueForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    return [projectList objectAtIndex:aRow];
}

@end
