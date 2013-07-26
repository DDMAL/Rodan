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
    var writtenGlyphs = [super writeSymbolName:newName];

    console.log("---- Calling classifierTableViewDelegate addGlyphsToClassifier ---");
    [classifierTableViewDelegate addGlyphsToClassifier:writtenGlyphs];
    [classifierTableViewDelegate reloadData];
}

@end
