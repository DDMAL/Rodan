
@implementation Result : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    created         @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
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
