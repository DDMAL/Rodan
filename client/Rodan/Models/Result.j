
@implementation Result : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    taskName        @accessors;
    CPString    created         @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['taskName', 'task_name']
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
        return @"/results/";
    }
}

@end
