@import <Ratatosk/Ratatosk.j>


@implementation Project : WLRemoteObject
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

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'resource_uri'],
        ['projectName', 'name'],
        ['description', 'description'],
        ['resourceURI', 'resource_uri']
    ];
}

@end
