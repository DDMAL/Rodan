@import "../Transformers/SymbolCollectionsTransformer.j"

@implementation Classifier : GameraGlyphs
{
    CPString       project           @accessors;
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
        ['pk',                'url'],
        ['project',           'project'],
        ['name',              'name',     nil, nil],
        ['symbolCollections', 'glyphs',   [[SymbolCollectionsTransformer alloc] init]]
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

