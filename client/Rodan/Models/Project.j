@import <Ratatosk/WLRemoteTransformers.j>
@import "User.j"
@import "Page.j"
@import "Workflow.j"

/* a full representation of a project, including arrays for the pages and workflows */
@implementation Project : WLRemoteObject
{
    CPString    pk                  @accessors;
    CPString    projectName         @accessors;
    CPString    projectCreator      @accessors;
    CPString    projectDescription  @accessors;
    CPObject    projectOwner        @accessors;
    CPString    resourceURI         @accessors;
    CPArray     pages               @accessors;
    CPArray     workflows           @accessors;
    CPDate      created             @accessors;
    CPDate      updated             @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        projectName = @"Untitled Project";
    }

    return self;
}

- (id)initWithCreator:(User)aCreator
{
    var self = [self init];
    [self setProjectCreator:aCreator];
    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectName', 'name'],
        ['projectDescription', 'description'],
        ['projectCreator', 'creator'],
        ['pages', 'pages', [WLForeignObjectsTransformer forObjectClass:Page]],
        ['workflows', 'workflows', [WLForeignObjectsTransformer forObjectClass:Workflow]],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true]
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

// - (CPString)remoteAction:(WLRemoteAction)anAction decodeResponseBody:(Object)aResponseBody
// {

//     var response = JSON.parse(aResponseBody);
//     console.log(response);
//     /*
//         setDirtProof ensures that updating this object does
//         not kick off a PATCH request for a change.
//     */
//     [WLRemoteObject setDirtProof:YES];
//     [self setPk:response.url];
//     [self setResourceURI:response.url];
//     [self setProjectOwner:response.creator];
//     [self setPages:response.pages];
//     [self setWorkflows:response.workflows];
//     [WLRemoteObject setDirtProof:NO];

//     CPLog("Done updating object");
//     console.log(self);

//     return aResponseBody;
// }
@end


/* A minimal representation of a project */
@implementation MinimalProject : WLRemoteObject
{
    CPString projectName        @accessors;
    CPString projectDescription @accessors;
    CPNumber pageCount          @accessors;
    CPNumber workflowCount      @accessors;
    CPString projectCreator     @accessors;
    CPDate   created            @accessors;
    CPDate   updated            @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        projectName = @"Untitled Project";
    }

    return self;
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

- (id)initWithCreator:(User)aCreator
{
    var self = [self init];
    [self setProjectCreator:aCreator];

    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['projectName', 'name'],
        ['projectDescription', 'description'],
        ['projectCreator', 'creator'],
        ['pageCount', 'page_count'],
        ['workflowCount', 'workflow_count'],
        ['created', 'created', [[WLDateTransformer alloc] init], true],
        ['updated', 'updated', [[WLDateTransformer alloc] init], true]
    ];
}

@end
