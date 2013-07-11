@import "../Models/Glyph.j"

@implementation GlyphsTransformer : CPObject //See WLRemoteTransformers.j in Ratatosk
{

}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

+ (Class)transformedValueClass
{
    return [Glyph class];
}

- (CPArray)transformedValue:(CPArray)jsonArrayOfGlyphs
{
    console.log("[GlyphsTransformer transformedValue].");
    return [Glyph objectsFromJson:jsonArrayOfGlyphs];
}

- (id)reverseTransformedValue:(CPArray)glyphs
{
    console.log("GlyphsTransformer reverseTransformedValue, calling [Glyph objectsToJson]");
    return [Glyph objectsToJson:glyphs];
}

@end
