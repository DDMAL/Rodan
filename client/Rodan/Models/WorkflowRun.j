@import <Ratatosk/WLRemoteObject.j>
@import "RunJob.j"
@import "User.j"

@implementation WorkflowRun : WLRemoteObject
{
    CPString    pk          @accessors;
    CPNumber    run         @accessors;
    CPArray     runJobs     @accessors;
    CPString    workflowURL @accessors;
    CPDate      created     @accessors;
    CPString    runCreator  @accessors;
    CPDate      updated     @accessors;
    BOOL        testRun     @accessors;

    CPString    testPageID  @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['runJobs', 'run_jobs', [WLForeignObjectsTransformer forObjectClass:RunJob]],
        ['workflowURL', 'workflow'],
        ['runCreator', 'creator', [WLForeignObjectTransformer forObjectClass:User]],
        ['run', 'run'],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true],
        ['testRun', 'test_run']
    ];
}

/* This modifies the request path so that we can launch a test run */
- (CPString)postPath
{
    var pathComponents = @"";
    if (testRun)
        pathComponents = "?test=true&page_id=" + testPageID;
    return [self remotePath] + pathComponents;
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
