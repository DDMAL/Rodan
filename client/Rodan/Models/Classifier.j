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

+ (CPArray)remoteProperties  //Ratatosk
{
    return [
        ['pk',          'url'],
        ['project',     'project'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}

- (CPString)remotePath  //Ratatosk
{
    if ([self pk])
        return [self pk];
    else
        return @"/classifiers/";  // remotePath is /classifiers/ when pk is not yet set because that's where we POST to.
}
@end
