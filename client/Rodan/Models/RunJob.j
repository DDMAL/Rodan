@import <Ratatosk/WLRemoteObject.j>

@implementation RunJob : WLRemoteObject
{
    CPString    pk          @accessors;
    CPNumber    sequence    @accessors;
    BOOL        needsInput  @accessors;
    CPArray     jobSettings @accessors;
    CPArray     result      @accessors;
    CPString    page        @accessors;
    CPDate      created     @accessors;
    CPDate      updated     @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url', nil, true],
        ['sequence', 'sequence'],
        ['needsInput', 'needs_input'],
        ['result', 'result'],
        ['page', 'page'],
        ['created', 'created', WLDateTransformer, true],
        ['updated', 'updated', WLDateTransformer, true]
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
        return @"/runjobs/";
    }
}

@end
