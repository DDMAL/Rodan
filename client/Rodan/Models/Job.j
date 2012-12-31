
@implementation Job : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    jobName  @accessors;
    JSObject    arguments   @accessors;
    JSObject    inputTypes   @accessors;
    JSObject    outputTypes  @accessors;
    CPString    category   @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['jobName', 'name'],
        ['arguments', 'arguments'],
        ['inputTypes', 'input_types'],
        ['outputTypes', 'output_types'],
        ['category', 'category'],
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
        return @"/jobs/";
    }
}
@end
