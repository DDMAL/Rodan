
@implementation Page : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    projectURI  @accessors;
    CPString    pageImage   @accessors;
    CPString    pageOrder   @accessors;
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
