@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>
@import "RodanAPIController.j"
@import "../Model/Project.j"

@implementation ProjectController : CPArrayController
{
    @outlet     CPTableView     theTable;
}

- (id)init
{
    if (self = [super init])
    {
        [self setObjectClass:Project];
        CPLog("Project controller init");
        [self fetchProjects];
    }
    return self;
}

- (id)awakeFromCib
{
    // [Project fetchProjects];
}

- (CPString)remoteActionContentType:(WLRemoteAction)anAction
{
    return @"application/json; charset=utf-8";
}

- (void)fetchProjects
{
    [WLRemoteAction schedule:WLRemoteActionGetType path:"project/" delegate:self message:"Loading projects…"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    p = [Project objectsFromJson:[anAction result].objects];
    [self addObjects:p];

    console.log([self objectClass]);
}

@end
