@import <Ratatosk/WLRemoteObject.j>
@import "Result.j"
@import "Page.j"

@implementation RunJob : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    jobName     @accessors;
    CPNumber    sequence    @accessors;
    BOOL        needsInput  @accessors;
    CPArray     jobSettings @accessors;
    CPArray     result      @accessors;
    // this uses a simplified page object instead of the full one via Ratatosk. It's just the page name and url.
    JSObject    page        @accessors;
    CPDate      created     @accessors;
    CPDate      updated     @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url', nil, true],
        ['jobName', 'job_name'],
        ['sequence', 'sequence'],
        ['needsInput', 'needs_input'],
        ['result', 'result', [WLForeignObjectsTransformer forObjectClass:Result]],
        ['page', 'page'],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true]
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
        return @"/runjobs/";
    }
}

@end
