@import <Ratatosk/Ratatosk.j>


@implementation Project : WLRemoteObject
{
    CPString    pk              @accessors;
    CPString    projectName     @accessors;
    CPString    projectDescription     @accessors;
    CPObject    projectOwner    @accessors;
    CPString    resourceURI     @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        CPLog("Initializing Project model");
        projectName = @"Project Name";
        projectDescription = @"Hi description";
    }
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
    if ([self pk])
    {
        return [self pk];
    }
    else
    {
        return @"/api/v1/project/";
    }
}

- (CPString)remoteAction:(WLRemoteAction)anAction decodeResponseBody:(Object)aResponseBody
{

    response = JSON.parse(aResponseBody);

    /*
        setDirtProof ensures that updating this object does
        not kick off a PATCH request for a change.
    */
    [WLRemoteObject setDirtProof:YES];
    [self setPk:response.resource_uri];
    [self setResourceURI:response.resource_uri];
    [self setProjectOwner:response.creator];
    [WLRemoteObject setDirtProof:NO];

    return aResponseBody;
}

@end
