
@implementation Page : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    projectURI      @accessors;
    CPString    imageFileSize   @accessors;
    CPString    pageImage       @accessors;
    CPString    pageOrder       @accessors;
    CPString    smallThumbURL   @accessors;
    CPString    mediumThumbURL  @accessors;
    CPString    largeThumbURL   @accessors;
    CPString    created         @accessors;
    CPString    creator         @accessors;
    BOOL        processed       @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectURI', 'project'],
        ['imageFileSize', 'image_file_size'],
        ['pageImage', 'page_image'],
        ['pageOrder', 'page_order'],
        ['smallThumbURL', 'small_thumb_url'],
        ['mediumThumbURL', 'medium_thumb_url'],
        ['largeThumbURL', 'large_thumb_url'],
        ['created', 'created'],
        ['creator', 'creator'],
        ['processed', 'processed']
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
