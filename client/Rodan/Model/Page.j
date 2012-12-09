
@implementation Page : WLRemoteObject
{
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectURI', 'project'],
        ['workflowURI', 'workflow'],
        ['filename', 'filename'],
        ['tag', 'tag'],
        ['pkName', 'pk_name'],
        ['sequence', 'sequence'],
        ['isReady', 'is_ready'],
        ['originalWidth', 'original_width'],
        ['originalHeight', 'original_height'],
        ['latestWidth', 'latest_width'],
        ['latestHeight', 'latest_height']
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
