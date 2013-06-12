@implementation SymbolCollection : CPObject
{
    CPString symbolName @accessors;
    CPMutableArray glyphList @accessors;
    int maxRows @accessors;
    int maxCols @accessors;
}
- (SymbolCollection)init
{
    self = [super init];
    [self setSymbolName:@""];
    [self setGlyphList:[[CPMutableArray alloc] init]];  // Mutable gives you addObject
    [self setMaxRows:0];
    [self setMaxCols:0];
    return self;
}
- (void)addGlyph:(Glyph)glyph
{
    [glyphList addObject:glyph];
    if ([glyph nRows] > [self maxRows])
        [self setMaxRows:[glyph nRows]];
    if ([glyph nCols] > [self maxCols])
        [self setMaxCols:[glyph nCols]];
}
- (void)removeGlyph:(Glyph)glyph
{
    console.log("In removeGlyph");
    console.log([[self glyphList] count]);
    console.log(glyph);

    [[self glyphList] removeObject:glyph];
    console.log([[self glyphList] count]);
    [self updateMaxes];
}
- (void)updateMaxes
{
    var glyphList_count = [glyphList count];
    [self setMaxRows:0];
    [self setMaxCols:0];
    for (var i = 0; i < glyphList_count; ++i)
    {
        if ([[self glyphList][i] nRows] > [self maxRows])
            [self setMaxRows:[[self glyphList][i] nRows]];
        if ([[self glyphList][i] nCols] > [self maxCols])
            [self setMaxCols:[[self glyphList][i] nCols]];
    }
}
@end
