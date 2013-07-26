@import "GameraGlyphs.j"

@implementation PageGlyphs : GameraGlyphs
{
    Classifier theClassifier @accessors;
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk];
    else
        return @"/pageglyphs/";
}

- (id)initWithJson:(id)jsonGameraGlyphs
{
    if (self = [super initWithJson:jsonGameraGlyphs])
    {
        [WLRemoteObject setDirtProof:YES];
        [glyphs makeObjectsPerformSelector:@"setPageGlyphsPk:" withObject:[self pk]];
        [WLRemoteObject setDirtProof:NO];
    }

    return self;
}

- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(id)aGlyph change:(CPDictionary)aChange context:(id)aContext
{
    [super observeValueForKeyPath:aKeyPath ofObject:aGlyph change:aChange context:aContext];

    var newName = [aChange valueForKey:@"CPKeyValueChangeNewKey"],
        oldName = [aChange valueForKey:@"CPKeyValueChangeOldKey"];

    if (aContext === _observingContext)
    {
        if (oldName !== newName && theClassifier)
        {
            [theClassifier addGlyph:aGlyph withName:newName];
        }
    }
}

@end
