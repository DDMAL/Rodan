@import <Ratatosk/WLRemoteObject.j>
@import "RunJob.j"

@implementation WorkflowRun : WLRemoteObject
{
    CPString    pk          @accessors;
    CPNumber    run         @accessors;
    CPArray     runJobs     @accessors;
    CPString    workflowURL @accessors;
    CPDate      created     @accessors;
    CPDate      updated     @accessors;
    BOOL        testRun     @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['runJobs', 'run_jobs', [WLForeignObjectsTransformer forObjectClass:RunJob]],
        ['workflowURL', 'workflow'],
        ['run', 'run'],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true],
        ['testRun', 'test_run']
    ];
}

- (CPString)remotePath
{
    if ([self pk])
    {
        return [self pk]
    }
    else
    {
        return @"/workflowruns/";
    }
}

@end
