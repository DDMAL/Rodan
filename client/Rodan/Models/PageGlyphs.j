@import "../Transformers/SymbolCollectionsTransformer.j"

@implementation PageGlyphs : GameraGlyphs
{

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
        ['pk',                'url'],
        ['name',              'name',   nil, nil],
        ['symbolCollections', 'glyphs', [[SymbolCollectionsTransformer alloc] init]]
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
