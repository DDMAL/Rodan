@import "../Delegates/GlyphsTableViewDelegate.j"

@implementation ClassifierTableViewDelegate : GlyphsTableViewDelegate
{

}

/*
    addGlyphsToClassifier:  Written to allow pageGlyphsTableViewDelegate to add glyphs
    to the classifier.

    Assumes that all the glyphs have the same name, because it's a safe assumption.
*/
- (void)addGlyphsToClassifier:(CPMutableArray)glyphs
{
    if ([glyphs count] === 0)
        return;

    var newBinIndex = [self _makeSymbolCollectionForName:[glyphs[0] idName]];

    for (var i = 0; i < [glyphs count]; ++i)
    {
        if (![self checkIfGlyph:glyphs[i] isAlreadyPresentIn:[theGameraGlyphs symbolCollections][newBinIndex]])
        {
            [[theGameraGlyphs symbolCollections][newBinIndex] addGlyph:glyphs[i]];
        }
    }

    [cvArrayControllers[newBinIndex] bind:@"contentArray" toObject:[theGameraGlyphs symbolCollections][newBinIndex] withKeyPath:@"glyphList" options:nil];
    [cvArrayControllers[newBinIndex] setSelectedObjects:glyphs];
    [theTableView reloadData];
}

- (void)checkIfGlyph:(Glyph)aGlyph isAlreadyPresentIn:(id)aSymbolCollection
{
    for (var i = 0; i < [[aSymbolCollection glyphList] count]; ++i)
    {
        if ([[aSymbolCollection glyphList][i] imageIsEqualToGlyph:aGlyph])
        {
            return true;
        }
    }
    return false;
}

@end
