@implementation SymbolTableDelegate : CPObject
{
    @outlet CPArrayController symbolArrayController;
}
- (void)initializeSymbols:(Classifier)aClassifier
{
    // Loop through all glyphs and build an array of symbols.

    // The symbols are used for the left sidebar view.

    // (Shouldn't the server do this?  Yeah.  Even if there aren't
    // symbols in the xml, it should send them as JSON.  Then the client
    // can maintain the array any time things are changed.)
    // Well... that doesn't help because the list of symbols doesn't
    // tell you the counts.  Add that to the XML?  Or just not depend on
    // that?  I think the latter is superior.  (slower but more robust)
    // Either way we will need this code because we need to support the case
    // where the server doesn't have a symbol list.
    var i = 0,
        glyphArray = [aClassifier glyphs],
        glyphCount = [glyphArray count],
        j = 0;

    [symbolArrayController setContent:[]];  // This is necessary if the user didn't 'close'
    for (; i < glyphCount; ++i)
    {
        var newSymbol = [[Symbol alloc] init:[glyphArray[i] idName]],
        //var found = [self reverseArrayContains:[symbolArrayController contentArray]:newSymbol];
            found = [self reverseArrayContains:[symbolArrayController contentArray] item:newSymbol];
        if (found < 0)
        {
            [symbolArrayController addObject:newSymbol];
        }
        else
        {
            [[symbolArrayController contentArray][found] increment];
        }
    }
    console.log([symbolArrayController contentArray]);
}
- (int)reverseArrayContains:(CPArray)array item:(id)thing
/* Intuitive except:
 - starts searching at the end
 - isEqual must be defined */
{
    var i = [array count];
    for (; i >= 0; --i)
    {
        if ([array[i] isEqual:thing])
        {
            return i;
        }
    }
    return -1;
}
- (void)close
{
    [symbolArrayController setContent:[]];
}
@end
