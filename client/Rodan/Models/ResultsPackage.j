@import <Ratatosk/WLRemoteTransformers.j>
@import "Page.j"
@import "WorkflowRun.j"

@implementation ResultsPackage : WLRemoteObject
{
    CPString    pk                  @accessors;
    CPString    downloadUrl         @accessors;
    CPString    name                @accessors;
    CPArray     pageUrls            @accessors;
    CPString    workflowRunUrl      @accessors;
    CPString    creator             @accessors;
    CPDate      created             @accessors;
    CPDate      updated             @accessors;
    CPNumber    percentCompleted    @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url', nil, true],
        ['downloadUrl', 'download_url', nil, true],
        ['name', 'name', nil, true],
        ['pageUrls', 'page_urls', nil, true],
        ['workflowRunUrl', 'workflow_run_url', nil, true],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true],
        ['creator', 'creator'],
        ['percentCompleted', 'percent_completed', nil, true]
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk]
    else
        return @"/resultspackages/";
}

@end
