/*
    Parent to Classifier and PageGlyphs
    (It's a little hard to read to have this tiny parent class to Classifier and PageGlyphs,
    but it is in fact necessary because GlyphsTableView uses polymorphism - it uses an object
    of type GameraGlyphs which can turn out to be a Classifier or PageGlyphs.)
*/

@implementation GameraGlyphs : WLRemoteObject
{
    CPString       pk                @accessors;
    CPMutableArray symbolCollections @accessors;
}

- (id)initWithJson:(id)js
{
    if (self = [super initWithJson:js])
    {
        for (var i = 0; i < [symbolCollections count]; ++i)
        {
            [symbolCollections[i] addObserver:self forKeyPath:@"glyphList" options:nil context:nil];
        }
    }

    return self;
}

- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(id)aSymbolCollection change:(CPDictionary)aChange context:(id)aContext
{
    console.log("GameraGlyphs observered a change to a symbol collection glyph list.");
    console.log(aChange);
}

@end
