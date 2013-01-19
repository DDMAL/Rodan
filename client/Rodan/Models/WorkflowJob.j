
// A WorkflowJob is an instantiation of a Job in a Workflow
@implementation WorkflowJob : WLRemoteObject
{
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
