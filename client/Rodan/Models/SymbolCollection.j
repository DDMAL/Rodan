@import "../Models/Glyph.j"

@implementation SymbolCollection : CPObject
{
    CPString          symbolName  @accessors;
    CPMutableArray    glyphList   @accessors;
    int               maxRows     @accessors;
    int               maxCols     @accessors;
    // CPArrayController cvArrayController;
}

- (SymbolCollection)init
{
    self = [super init];

    if (self)
    {
        [self setSymbolName:@""];
        [self setGlyphList:[[CPMutableArray alloc] init]];  // Mutable gives you addObject
        [self setMaxRows:0];
        [self setMaxCols:0];
    }

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
    [[self glyphList] removeObject:glyph];
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

- (void)stringAndCountOutput
{
    return [[self symbolName] stringByAppendingFormat:@" (%d)", [[self glyphList] count]];
}

- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(id)aGlyph change:(CPDictionary)aChange context:(id)aContext
{
    console.log("SymbolCollection observered a change to a the " + aKeyPath + " of a glyph:");
    console.log(aChange);
}

@end
