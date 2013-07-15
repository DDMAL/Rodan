@import "../Models/Glyph.j"

@implementation GlyphsTransformer : CPObject //See WLRemoteTransformers.j in Ratatosk
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
    // console.log("GlyphsTransformer calling Glyph objectsFromJson!");
    // console.log(jsonArrayOfGlyphs);
    // var retval = [Glyph objectsFromJson:jsonArrayOfGlyphs];
    // console.log("GlyphsTransformer returning " + retval);
    return [Glyph objectsFromJson:jsonArrayOfGlyphs];
}

- (id)reverseTransformedValue:(CPArray)glyphs
{
    return [Glyph objectsToJson:glyphs];
}

@end
