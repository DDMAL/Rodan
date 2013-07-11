@import "Glyph.j"

/*
    The symbol collection has two important field:
        symbolName - a kind of neume
        glyphList  - the list of images with that name

    I made the symbolCollection in charge of the collection view array controller as a design choice
    because it makes the tasks associated with renaming a glyph possible.  It's a logical design because
    the cvArrayController controls the glyphList array.  The symbolCollection 'observes' the glyph
    idName and keeps the cvArrayController in sync when a glyph's name changes.
*/
@implementation SymbolCollection : CPObject
{
    CPString          symbolName        @accessors;
    CPMutableArray    glyphList         @accessors;
    int               maxRows           @accessors;
    int               maxCols           @accessors;
    CPArrayController cvArrayController @accessors;
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
        cvArrayController = [[CPArrayController alloc] init];
        [cvArrayController bind:@"contentArray" toObject:self withKeyPath:@"glyphList" options:nil];
        [cvArrayController setAvoidsEmptySelection:NO];
        [cvArrayController setPreservesSelection:YES];
        [cvArrayController rearrangeObjects];
        [cvArrayController setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
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

    [cvArrayController bind:@"contentArray" toObject:self withKeyPath:@"glyphList" options:nil];
    [cvArrayController setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
}

- (void)removeGlyph:(Glyph)glyph
{
    [[self glyphList] removeObject:glyph];
    [self updateMaxes];
    [cvArrayController bind:@"contentArray" toObject:self withKeyPath:@"glyphList" options:nil];
    [cvArrayController setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
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
