@import <AppKit/AppKit.j>
@import "RodanAPIController.j"
@import "../Model/Project.j"

@implementation ProjectController : CPArrayController
{
    CPString    allProjectsNotification;

    @outlet     CPWindow    addProjectWindow;
    @outlet     CPTextField projectName;
    @outlet     CPTextField projectDescription;
    @outlet     CPTableView theTable;
}

- (id)awakeFromCib
{
    CPLog("Initializing");
    allProjectsNotification = @"didReceiveAllProjects";
    notificationCenter = [CPNotificationCenter defaultCenter];
    [notificationCenter addObserver:self selector:@selector(didReceiveProjectList:) name:allProjectsNotification object:nil]
    [self getAllProjects];
}

- (IBAction)addProject:(id)aSender
{
    CPLog("Name: " + [projectName objectValue]);
    CPLog("Description: " + [projectDescription objectValue]);
    [addProjectWindow close];

    [self add:aSender];
}

- (IBAction)add:(id)aSender
{
    [super add:aSender];
}

- (IBAction)remove:(id)aSender
{
    [super remove:aSender];
}

- (IBAction)removeAtSelectedIndex:(id)aSender
{
    CPLog("Removing at " + [self selectionIndex]);
    [self removeObjectAtArrangedObjectIndex:[self selectionIndex]];

}

- (void)didReceiveProjectList:(id)aNotification
{
    data = JSON.parse([aNotification object]);
    for (var i = 0; i < data.objects.length; i++)
    {
        p = [Project initWithJSONObject:data.objects[i]];
        [self addObject:p];
    };
}

/* Rodan Projects API */

- (void)getAllProjects
{
    conn = [[RodanAPIController alloc] init];
    [conn setRequestURI:"/api/v1/project"]
    [conn setCallbackNotification:allProjectsNotification];
    [conn execute];
    // [ initWithRequest:@"project" notification:allProjectsNotification];
}

- (void)getProjectAtURI:(CPString)aURI
{
    // [RodanAPIController initWithRequest:@"project" notification:singleProjectNotification];
}

- (void)createNewProject:(CPString)aName withDescription:(CPString)aDescription
{
    // POST
}

- (void)deleteProjectAtURI:(CPString)aURI
{
    // DELETE
}

- (void)updateProjectAtURI:(CPString)aURI setName:(CPString)aName setDescription:(CPString)aDescription
{
    //
}
@end
