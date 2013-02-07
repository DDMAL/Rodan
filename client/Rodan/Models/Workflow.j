
@implementation Workflow : WLRemoteObject
{
    CPString    workflowName    @accessors;
    CPString    project         @accessors;
    CPArray    jobs            @accessors;
    CPArray    pages           @accessors;
    CPString    description     @accessors;
    BOOL        hasStarted      @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        workflowName = @"Untitled";
        jobs = [];
        pages = [];
        hasStarted = NO;
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
