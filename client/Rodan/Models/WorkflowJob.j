
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
    BOOL        needsInput      @accessors;
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
        ['jobName', 'name'],
        ['job', 'job'],
        ['sequence', 'sequence'],
        ['jobSettings', 'job_settings'],
        ['inputPixels', 'input_pixel_types'],
        ['outputPixels', 'output_pixel_types'],
        ['jobType', 'job_type'],
        ['needsInput', 'needs_input']

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
@end
