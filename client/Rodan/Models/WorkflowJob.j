@import "../Transformers/JobArgumentsTransformer.j"

// A WorkflowJob is an instantiation of a Job in a Workflow
@implementation WorkflowJob : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    workflow        @accessors;
    CPString    jobName         @accessors;
    CPString    job             @accessors;
    CPNumber    sequence        @accessors;
    CPNumber    jobType         @accessors;
    CPArray     jobSettings     @accessors;
    CPArray     inputPixels     @accessors;
    CPArray     outputPixels    @accessors;
    CPString    jobDescription  @accessors;
}

// + (WorkflowJob)initWithJob:(CPString)aJobURI forWorkflow:(CPString)aWorkflowURI
// {
//     var self = [[WorkflowJob alloc] init];
//     [self setJob:aJobURI];
//     [self setWorkflow:aWorkflowURI];

//     return self;
// }

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['workflow', 'workflow'],
        ['jobName', 'job_name', nil, true],  // nil transformer, true read-only
        ['jobDescription', 'job_description', nil, true],  // nil transformer, true read-only
        ['job', 'job'],
        ['sequence', 'sequence'],
        ['jobSettings', 'job_settings', [[JobArgumentsTransformer alloc] init]],
        ['inputPixels', 'input_pixel_types'],
        ['outputPixels', 'output_pixel_types'],
        ['jobType', 'job_type'],
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
        return @"/workflowjobs/";
    }
}

- (void)removeFromWorkflow
{
    [self setWorkflow:nil];
    [self ensureSaved];
}

@end
