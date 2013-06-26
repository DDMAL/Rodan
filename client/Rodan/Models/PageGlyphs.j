@import "../Transformers/SymbolCollectionsTransformer.j"

@implementation PageGlyphs : GameraGlyphs
{

}

+ (CPArray)remoteProperties
{
    return [
        ['pk',                'url'],
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
