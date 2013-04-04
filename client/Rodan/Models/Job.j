@import "../Transformers/JobArgumentsTransformer.j"

@implementation Job : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    jobName         @accessors;
    CPArray     settings        @accessors;
    CPArray     inputTypes      @accessors;
    CPArray     outputTypes     @accessors;
    CPString    category        @accessors;
    CPString    description     @accessors;
    BOOL        isEnabled       @accessors;
    BOOL        isInteractive   @accessors;

    CPImage     sourceListIcon  @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        sourceListIcon = [[CPImage alloc] initWithContentsOfFile:[[CPBundle mainBundle] pathForResource:@"job-sourcelist-icon.png"]
                                  size:CGSizeMake(16.0, 16.0)];

    }
    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['jobName', 'job_name'],
        // ['arguments', 'arguments', [[JobArgumentsTransformer alloc] init]],
        ['settings', 'settings'],
        ['description', 'description'],
        ['inputTypes', 'input_types'],
        ['outputTypes', 'output_types'],
        ['category', 'category'],
        ['isEnabled', 'enabled'],
        ['isInteractive', 'interactive']
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
