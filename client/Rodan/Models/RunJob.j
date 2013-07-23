@import <Ratatosk/WLRemoteObject.j>
@import "Result.j"
@import "Page.j"
@import "../Transformers/RunJobSettingsTransformer.j"

RUNJOB_STATUS_FAILED = -1,
RUNJOB_STATUS_NOTRUNNING = 0,
RUNJOB_STATUS_RUNNING = 1,
RUNJOB_STATUS_WAITINGFORINPUT = 2,
RUNJOB_STATUS_RUNONCEWAITING = 3,
RUNJOB_STATUS_HASFINISHED = 4,
RUNJOB_STATUS_CANCELLED = 9;

@implementation RunJob : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    jobName         @accessors;
    CPNumber    sequence        @accessors;
    CPNumber    status          @accessors;
    BOOL        needsInput      @accessors;
    CPString    workflowName    @accessors;
    CPArray     jobSettings     @accessors;
    CPArray     result          @accessors;
    // this uses a simplified page object instead of the full one via Ratatosk. It's just the page name and url.
    JSObject    page            @accessors;
    CPDate      created         @accessors;
    CPDate      updated         @accessors;
    CPString    errorSummary    @accessors;
    CPString    errorDetails    @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url', nil, true],
        ['jobName', 'job_name'],
        ['sequence', 'sequence'],
        ['status', 'status'],
        ['needsInput', 'needs_input'],
        ['workflowName', 'workflow_name'],
        ['jobSettings', 'job_settings', [[RunJobSettingsTransformer alloc] init]],
        ['result', 'result', [WLForeignObjectsTransformer forObjectClass:Result]],
        ['page', 'page', [WLForeignObjectTransformer forObjectClass:Page]],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true],
        ['errorSummary', 'error_summary'],
        ['errorDetails', 'error_details']
    ];
}

/**
 * Returns the last component of the pk URL, which is the UUID of the RunJob.
 * If pk is nil, returns nil.
 */
- (CPString)getUUID
{
    var runJobUUID = nil;
    if ([self pk])
    {
        runJobUUID = [pk lastPathComponent];
    }
    return runJobUUID;
}

/**
 * Convenience method for enabling/disabling "View Error Details" button.
 */
- (BOOL)didFail
{
    return [self status] == -1;
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk]
    else
        return @"/runjobs/";
}

- (BOOL)canRunInteractive
{
    return [self status] == 2 || [self status] == 3;
}

@end
