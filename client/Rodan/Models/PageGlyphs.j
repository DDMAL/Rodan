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

+ (CPArray)remoteProperties
{
    return [
        ['pk',          'url'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk];
    else
        return @"/pageglyphs/";
}
@end
