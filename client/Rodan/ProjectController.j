@import <AppKit/AppKit.j>
@import "Model/Project.j"

@implementation ProjectController : CPObject
{
    @outlet     CPWindow        theWindow;
    @outlet     CPTextField     projectName;
    @outlet     CPTextField     projectDescription;
                CPMutableArray  projectsArray   @accessors;
    @outlet     CPTableView     selectProjectsTable;
}

- (id)init
{
    if (self = [super init])
    {
        selectProjectsTable = [[CPTableView alloc] init];
        projectsArray = [[CPMutableArray alloc] init];
        proj = [[Project alloc] init];
        [projectsArray addObject:proj];
    }
    return self;
}

- (IBAction)saveProject:(id)aSender
{
    CPLog("Save Project");
}

- (IBAction)openProject:(id)aSender
{
    CPLog("Open Project");
}

- (IBAction)newProject:(id)aSender
{
    CPLog("New project");
    proj = [[Project alloc] init];
    [projectsArray addObject:proj];
    [selectProjectsTable reloadData];
    console.log([projectsArray count]);
}

@end
