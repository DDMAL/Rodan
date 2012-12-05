@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "RodanAPIController.j"
@import "../Model/Project.j"

@implementation ProjectController : CPObject
{
    @outlet     CPTableView         projectChooseTable;
    @outlet     CPArrayController   projectArrayController;
}

- (id)init
{
    if (self = [super init])
    {
        CPLog("Project controller init");
        [self fetchProjects];
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
    [WLRemoteAction schedule:WLRemoteActionGetType path:"project/" delegate:self message:"Loading projects"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    CPLog("Action did Finish");
    console.log(anAction);
    p = [Project objectsFromJson:[anAction result].objects];
    [projectArrayController addObjects:p];
    console.log([projectArrayController contentArray]);
}

- (IBAction)addProject:(id)aSender
{
    // p = [[Project alloc] init];
    // console.log([p remotePath]);
    p = [[Project alloc] initWithJson:{"name": "My newly created project", "description": "A great description", "creator": "/api/v1/user/1/"}];
    [projectArrayController addObject:p];
    [p ensureCreated];
}

- (IBAction)getContentArray:(id)aSender
{
}

@end
