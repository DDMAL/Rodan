@import <Ratatosk/Ratatosk.j>


@implementation Project : WLRemoteObject
{
    CPString    projectName     @accessors;
    CPString    projectDescription     @accessors;
    CPString    projectOwner           @accessors;
    CPString    resourceURI     @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        CPLog("Initializing Project model");
        projectName = @"Project Name"
    }

    console.log(self);

    return self;
}

+ (CPArray)remoteProperties
{
    CPLog("Remote Properties Called");
    return [
        ['pk', 'resource_uri'],
        ['projectName', 'name'],
        ['projectDescription', 'description'],
        ['projectOwner', 'creator'],
        ['resourceURI', 'resource_uri']
    ];
}

- (CPString)remotePath
{
    return "project/";
}
@end
