@import "WorkflowJob.j"
@import "Job.j"

@implementation Workflow : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    uuid            @accessors;
    CPString    workflowName    @accessors;
    CPString    projectURI      @accessors;
    CPArray     jobs            @accessors;
    CPArray     workflowJobs    @accessors;
    CPArray     pages           @accessors;
    CPString    description     @accessors;
    BOOL        hasStarted      @accessors;

    CPImage     sourceListIcon  @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        workflowName = @"Untitled";
        jobs = [];
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
        ['workflowName', 'name'],
        ['projectURI', 'project'],
        ['jobs', 'jobs', [WLForeignObjectOrObjectsTransformer forObjectClass:Job]],
        ['workflowJobs', 'workflowjob_set', [WLForeignObjectOrObjectsTransformer forObjectClass:WorkflowJob]],
        ['pages', 'pages'],
        ['description', 'description'],
        ['hasStarted', 'has_started'],
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
        return @"/workflows/";
    }
}
@end
