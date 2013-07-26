@import "../Delegates/GlyphsTableViewDelegate.j"

@implementation ClassifierTableViewDelegate : GlyphsTableViewDelegate
{

}

/*
    addGlyphsToClassifier:  Written to allow pageGlyphsTableViewDelegate to add glyphs
    to the classifier.

    Assumes that all the glyphs have the same name, because it's a safe assumption.
*/

// THIS FUNCTION WAS USED BEFORE THE MODEL WAS SMART ENOUGH
// (Now this isn't the Delegate's job, it's the model's job.)
// - (void)addGlyphsToClassifier:(CPMutableArray)glyphs
// {
//     if ([glyphs count] === 0)
//         return;

//     var newBinIndex = [self _makeSymbolCollectionForName:[glyphs[0] idName]],
//         symbolCollection = [theGameraGlyphs symbolCollections][newBinIndex],
//         cvArrayController = [symbolCollection cvArrayController];

//     for (var i = 0; i < [glyphs count]; ++i)
//     {
//         if (![self checkIfGlyph:glyphs[i] isAlreadyPresentIn:[theGameraGlyphs symbolCollections][newBinIndex]])
//         {
//             [symbolCollection addGlyph:glyphs[i]];
//         }
//     }

//     [cvArrayController setSelectedObjects:glyphs];
//     [theTableView reloadData];
// }

// - (void)checkIfGlyph:(Glyph)aGlyph isAlreadyPresentIn:(id)aSymbolCollection
// {
//     for (var i = 0; i < [[aSymbolCollection glyphList] count]; ++i)
//     {
//         if ([[aSymbolCollection glyphList][i] isEqualTo:aGlyph])
//         {
//             return true;
//         }
//     }
//     return false;
// }

- (void)addGlyphsToClassifier:(CPMutableArray)glyphs
{
    // [WLRemoteObject setDirtProof:YES];
    // [glyphs makeObjectsPerformSelector:@"setClassifierPk:" withObject:[theGameraGlyphs pk]];
    console.log("classifierTableViewDelegate done setting classifier pks");

    for (var i = 0; i < [glyphs count]; i++)
    {
        // [theGameraGlyphs putGlyph:glyphs[i] intoSymbolCollection:[glyphs[i] idName]];
        [theGameraGlyphs addGlyph:glyphs[i]];  // Classifier.j
    }

    // [glyphs makeObjectsPerformSelector:@"ensureCreated"];
    // [WLRemoteObject setDirtProof:NO];
}

- (void)writeSymbolName:(CPString)newName
{
    // Look for the glyph in the page glyph view and write it (... old algorithm)

    // Write the glyph in classifier view
    [super writeSymbolName:newName];
    [theOtherTableViewDelegate reloadData];  // Ideally, only happens if the glyph were in the other table view (perhaps that could be done by observing... Delegates observing all the glyphs... not sure I want that.)
}

@end
