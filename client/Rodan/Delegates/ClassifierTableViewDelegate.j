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
    console.log("classifierTableViewDelegate done setting classifier pks");

    for (var i = 0; i < [glyphs count]; i++)
    {
        [theGameraGlyphs addGlyph:glyphs[i]];  // Classifier.j
    }

}

- (void)writeSymbolName:(CPString)newName
{

    [super writeSymbolName:newName];
    [theOtherTableViewDelegate reloadData];  // Ideally, only happens if the glyph were in the other table view (perhaps that could be done by observing... Delegates observing all the glyphs... not sure I want that.)
}

@end
