@import "WorkflowJob.j"
@import "WorkflowRun.j"
@import "Job.j"
@import "Page.j"

@implementation Workflow : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    uuid            @accessors;
    CPString    workflowName    @accessors;
    CPString    projectURL      @accessors;
    CPNumber    runs            @accessors;
    CPArray     workflowJobs    @accessors;
    CPArray     workflowRuns    @accessors;
    CPArray     pages           @accessors;
    CPString    description     @accessors;
    BOOL        hasStarted      @accessors;
    CPString    workflowCreator @accessors;
    CPImage     sourceListIcon  @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        workflowName = @"Untitled";
        pages = [];
        hasStarted = NO;

        sourceListIcon = [[CPImage alloc] initWithContentsOfFile:[[CPBundle mainBundle] pathForResource:@"workflow-sourcelist-icon.png"]
                                          size:CGSizeMake(16.0, 16.0)]
    }

    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['uuid', 'uuid'],
        ['runs', 'runs', nil, true],
        ['workflowName', 'name'],
        ['projectURL', 'project'],
        ['workflowJobs', 'workflow_jobs', [WLForeignObjectsTransformer forObjectClass:WorkflowJob]],
        ['workflowRuns', 'workflow_runs', [WLForeignObjectsTransformer forObjectClass:WorkflowRun]],
        ['pages', 'pages', [WLForeignObjectsTransformer forObjectClass:Page]],
        ['description', 'description'],
        ['hasStarted', 'has_started'],
        ['workflowCreator', 'creator']
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk]
    else
        return @"/workflows/";
}

- (void)addPage:(id)aPage
{
    // adds a page to a workflow
    console.log("Adding a page to the workflow");
}

- (void)addPages:(CPArray)pages
{
    console.log("Adding pages to workflow");
    // adds lots of pages to a workflow
}

- (void)addJob:(id)aJob
{
    // add a job to a workflow
}

- (void)addJobs:(CPArray)jobs
{
    // add lots of jobs to a workflow
}

/**
 * Touches it so job settings are saved.
 */
- (void)touchWorkflowJobs
{
    [workflowJobs makeObjectsPerformSelector:@selector(makeAllDirty)];
    [workflowJobs makeObjectsPerformSelector:@selector(ensureSaved)];
}
@end
