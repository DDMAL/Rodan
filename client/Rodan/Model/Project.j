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
    }
    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectName', 'name'],
        ['projectDescription', 'description'],
        ['projectOwner', 'creator'],
        ['resourceURI', 'url']
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
        return @"/projects/";
    }
}

- (CPString)remoteAction:(WLRemoteAction)anAction decodeResponseBody:(Object)aResponseBody
{

    response = JSON.parse(aResponseBody);
    console.log(response);
    /*
        setDirtProof ensures that updating this object does
        not kick off a PATCH request for a change.
    */
    [WLRemoteObject setDirtProof:YES];
    [self setPk:response.url];
    [self setResourceURI:response.url];
    [self setProjectOwner:response.creator];
    [WLRemoteObject setDirtProof:NO];

    CPLog("Done updating object");
    console.log(self);

    return aResponseBody;
}

@end
