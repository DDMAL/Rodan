@import "../Delegates/GlyphsTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"

@implementation PageGlyphsTableViewDelegate : GlyphsTableViewDelegate
{
    ClassifierTableViewDelegate classifierTableViewDelegate;
}

- (void)init
{
    self = [super init];

    if (self)
    {
        classifierTableViewDelegate = theOtherTableViewDelegate;
    }

    return self;
}

- (void)writeSymbolName:(CPString)newName
{
    // Look for the glyph in the ClassifierTableView, then select it and call writeSymbolName on the classifierTableView
    // But, ClassifierController already does that.
    // Well, how about just calling it on the pageGlyph table view first?  That'd work.  It's a bit hairy, so
    // it should be put in its own function in the classifierController.

    // (Be sure that "shift is pressed" when
    // you add the selection on the other view(?) NOPE:  Nothing else should be selected anyway!)

    // Well, if you select that glyph, it'll nullify the current view.  So, just do it without selecting.
    // Give the glyph directly to a write function that moves it and syncs the two cv's and the symbol
    // collection.  It'd be nice if the other algorithm used the same function, but not critical.

    // classifierTableViewDelegate

    // var writtenGlyphs = [super writeSymbolName:newName];
    // [classifierTableViewDelegate addGlyphsToClassifier:writtenGlyphs];

    [super writeSymbolName:newName];
    [classifierTableViewDelegate reloadData];  // Aha... the classifierTableViewDelegate must do the same thing.
        // heheheh, this part can be generic too... just call theOtherTableViewDelegate from the parent!

    // Ok, just need to POST... that's done by the model too.
}

@end
