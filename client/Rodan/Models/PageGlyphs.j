@import "../Transformers/GlyphTransformer.j"

@implementation PageGlyphs : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    name        @accessors;
    CPArray     glyphs      @accessors;
}

- (id)initWithName:(CPString)aName
{
    if (self = [self init])
    {
        [self setName:aName];
    }
    return self;
}

+ (CPArray)remoteProperties  //Ratatosk
{
    return [
        ['pk',          'url'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}

- (CPString)remotePath  //Ratatosk
{
    if ([self pk])
        return [self pk];
    else
        return @"/pageglyphs/";  // remotePath is /classifiers/ when pk is not yet set because that's where we POST to.
}
@end
