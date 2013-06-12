@import "../Models/Glyph.j"

@implementation GlyphTransformer : CPObject //See WLRemoteTransformers.j in Ratatosk
{

}

+ (BOOL)allowsReverseTransformation
{
    return YES;  // Change to YES to save glyphs
}

+ (Class)transformedValueClass
{
    return [Glyph class];
}

- (CPArray)transformedValue:(CPArray)jsonArrayOfGlyphs
{
    return [Glyph objectsFromJson:jsonArrayOfGlyphs];
}

- (id)reverseTransformedValue:(CPArray)glyphs
{
    return [Glyph objectsToJson:glyphs];
}

@end
