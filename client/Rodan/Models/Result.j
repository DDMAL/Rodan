@import <Ratatosk/WLRemoteTransformers.j>
@import "RunJob.j"

@implementation Result : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    resultURL       @accessors;
    CPString    runJobName      @accessors;
    CPString    mediumThumbURL  @accessors;
    CPDate      created         @accessors;
    CPDate      updated         @accessors;
    RunJob      runJob          @accessors;
    CPString    thumbURL        @accessors;
    BOOL        processed       @accessors;
    CPString    result          @accessors;

    // CPString    taskName        @accessors;
    // CPString    created         @accessors;
    // JSObject    page            @accessors;
    // JSObject    workflowJob     @accessors;
    // CPString    resultURI       @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url', nil, true],
        ['runJob', 'run_job', nil, true],
        ['runJobName', 'run_job_name'],
        ['resultURL', 'result', nil, true],
        ['thumbURL', 'medium_thumb_url'],
        ['mediumThumbURL', 'medium_thumb_url'],
        ['result', 'result'],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true],
        ['processed', 'processed']
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk]
    else
        return @"/results/";
}

@end
