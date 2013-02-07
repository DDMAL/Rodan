
@implementation Workflow : WLRemoteObject
{
    CPString    workflowName    @accessors;
    CPString    project         @accessors;
    CPString    jobs            @accessors;
    CPString    pages           @accessors;
    CPString    description     @accessors;
    BOOL        hasStarted      @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        workflowName = @"Untitled";
    }
    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['workflowName', 'name'],
        ['project', 'project'],
        ['jobs', 'jobs'],
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
