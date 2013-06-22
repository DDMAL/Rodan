@import "../Delegates/GlyphsTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"

@implementation PageGlyphsTableViewDelegate : GlyphsTableViewDelegate
{
    @outlet ClassifierTableViewDelegate classifierTableViewDelegate;
}

- (void)writeSymbolName:(CPString)newName
{
    var writtenGlyphs = [super writeSymbolName:newName];
    [classifierTableViewDelegate addGlyphsToClassifier:writtenGlyphs];
}
@end
