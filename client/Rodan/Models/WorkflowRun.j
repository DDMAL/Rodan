@import <Ratatosk/WLRemoteObject.j>
@import "RunJob.j"
@import "User.j"

@implementation WorkflowRun : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    uuid        @accessors;
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
        ['uuid', 'uuid'],
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


/**
 * We override WLRemoteObject::isEqual to make sure that other WLRemoteObjects that have this class as a member (e.g. Workflow)
 * don't just look at the PK and class (which is what isEqual does by default).
 *
 * We can create a custom list of fields that override WLRemoteObject equality, but for now it's just the 'updated' member.
 */
- (BOOL)isEqual:(id)aObject
{
    if ([super isEqual:aObject])
    {
        if ([self updated] === [aObject updated])
        {
            return YES;
        }
    }
    return NO;
}

@end
