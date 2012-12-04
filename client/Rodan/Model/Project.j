
@implementation Project : CPObject
{
    CPString    projectName     @accessors;
    CPString    description     @accessors;
    CPString    owner           @accessors;
    CPString    resourceURI     @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        CPLog("Initializing Project model");
    }
    return self;
}

+ (id)initWithJSONObject:(id)anObject
{
    project = [[Project alloc] init];

    [project setProjectName:anObject.name];
    [project setDescription:anObject.description];
    [project setResourceURI:anObject.resource_uri];

    return project;
}

@end
