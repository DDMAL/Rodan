
@implementation Page : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    projectURI  @accessors;
    CPString    pageImage   @accessors;
    CPString    pageOrder   @accessors;
    CPString    smallThumbURL  @accessors;
    CPString    mediumThumbURL   @accessors;
    CPString    largeThumbURL   @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectURI', 'project'],
        ['pageImage', 'page_image'],
        ['pageOrder', 'page_order'],
        ['smallThumbURL', 'small_thumb_url'],
        ['mediumThumbURL', 'medium_thumb_url'],
        ['largeThumbURL', 'large_thumb_url'],
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
