@import <Ratatosk/WLRemoteTransformers.j>
@import "RunJob.j"

@implementation Result : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    resultURL       @accessors;
    CPDate      created         @accessors;
    CPDate      updated         @accessors;
    RunJob      runJob          @accessors;
    CPString    thumbURL        @accessors;

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
        ['resultURL', 'result', nil, true],
        ['thumbURL', 'medium_thumb_url'],
        ['created', 'created', [WLDateTransformer alloc], true],
        ['updated', 'updated', [WLDateTransformer alloc], true]
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
        return @"/results/";
    }
}

@end
