
@implementation Workflow : WLRemoteObject
{
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['name', 'name'],
        ['jobs', 'jobs'],
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
