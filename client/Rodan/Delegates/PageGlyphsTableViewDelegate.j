@import "../Delegates/GlyphsTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"

@implementation PageGlyphsTableViewDelegate : GlyphsTableViewDelegate
{

}

- (void)writeSymbolName:(CPString)newName
{
    var writtenGlyphs = [super writeSymbolName:newName];
    [theOtherTableViewDelegate addGlyphsToClassifier:writtenGlyphs];
    [theOtherTableViewDelegate reloadData];
}

@end
