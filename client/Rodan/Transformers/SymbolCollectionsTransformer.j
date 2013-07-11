@import "../Models/SymbolCollection.j"
@import "../Models/Glyph.j"

@implementation SymbolCollectionsTransformer : CPObject
{

}
+ (BOOL)allowsReverseTransformation
{
    return YES;
}

+ (Class)transformedValueClass
{
    return [CPMutableArray class];
}

- (CPArray)transformedValue:(CPArray)jsonArrayOfGlyphs
{
    console.log("Ratatosk is making new objects.");
    var i = 0,
        glyphs = [Glyph objectsFromJson:jsonArrayOfGlyphs],
        glyphs_count = [glyphs count],
        prevGlyphName = nil,
        symbolCollectionArray = [[CPMutableArray alloc] init],
        symbolCollection = nil;

    for (i = 0; i < glyphs_count; ++i)
    {
        var glyphName = [glyphs[i] idName];
        if (prevGlyphName === nil || prevGlyphName !== glyphName)
        {
            symbolCollection = [[SymbolCollection alloc] init];
            [symbolCollection setSymbolName:glyphName];
            [symbolCollectionArray addObject:symbolCollection];
        }
        [symbolCollection addGlyph:glyphs[i]];
        [glyphs[i] addObserver:symbolCollection forKeyPath:@"idName" options:nil context:nil];
        prevGlyphName = glyphName;
    }

    return symbolCollectionArray;
}

- (id)reverseTransformedValue:(CPArray)symbolCollections
{
    var i = 0,
        symbolCollectionsCount = [symbolCollections count],
        glyphs = [[CPMutableArray alloc] init];

    for (; i < symbolCollectionsCount; ++i)
    {
        [glyphs addObjectsFromArray:[symbolCollections[i] glyphList]];
    }
    return [Glyph objectsToJson:glyphs];
}
@end
