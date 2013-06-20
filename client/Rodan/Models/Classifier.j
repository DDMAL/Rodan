@import "../Transformers/GlyphTransformer.j"

@implementation Classifier : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    project     @accessors;
    CPString    name        @accessors;
    CPArray     glyphs      @accessors;
}

- (id)initWithName:(CPString)aName andProjectPk:(CPString)aProjectPk
{
    if (self = [self init])
    {
        [self setName:aName];
        [self setProject:aProjectPk];
    }
    return self;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk',          'url'],
        ['project',     'project'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk];
    else
        return @"/classifiers/";
}
@end
