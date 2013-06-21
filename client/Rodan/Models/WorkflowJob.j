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
        return [self pk]
    else
        return @"/workflowjobs/";
}

- (void)removeFromWorkflow
{
    [self setWorkflow:nil];
    [self ensureSaved];
}

- (CPString)shortJobName
{
    var shortName = jobName,
        splitString = [shortName componentsSeparatedByString:"."];
    if ([splitString count] > 1)
    {
        shortName = [[splitString lastObject] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        return [shortName capitalizedString];
    }
    return shortName;
}

@end
