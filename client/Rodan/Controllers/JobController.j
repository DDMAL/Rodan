@import "../Models/Job.j"
@import "../Models/TreeNode.j"

@global RodanDidLoadJobsNotification
@global RodanJobTreeNeedsRefresh

@implementation JobController : CPObject
{
    @outlet CPArrayController   jobArrayController;
}

- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (void)fetchJobs
{

    [WLRemoteAction schedule:WLRemoteActionGetType path:"/jobs/?enabled=1" delegate:self message:"Loading jobs"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    if ([anAction result])
    {
        var j = [Job objectsFromJson:[anAction result]];
        [jobArrayController addObjects:j];
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadJobsNotification
                                              object:[anAction result]];
    }
}
@end
