
// A WorkflowJob is an instantiation of a Job in a Workflow
@implementation WorkflowJob : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    workflow        @accessors;
    CPString    job             @accessors;
    CPNumber    sequence        @accessors;
    CPArray     jobSettings     @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['workflow', 'workflow'],
        ['job', 'job'],
        ['sequence', 'sequence'],
        ['jobSettings', 'job_settings'],
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
