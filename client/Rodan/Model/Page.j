
@implementation Page : WLRemoteObject
{
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectURI', 'project'],
        ['pageImage', 'page_image'],
        ['pageOrder', 'page_order'],
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
        return @"/pages/";
    }
}
@end
