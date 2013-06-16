@implementation Symbol : CPObject
{
    CPString symbolName @accessors;
    int count @accessors;
}

- (Symbol)initWithName:(CPString)aSymbolName
{
    [self setSymbolName:aSymbolName];
    [self setCount:1];
    return self;
}
- (void)increment
{
    [self setCount:[self count] + 1];
}
- (Boolean)isEqual:(Symbol)aSymbol
{
    return [self symbolName] === [aSymbol symbolName];
}
- (CPString)stringAndCountOutput
{
    return [[self symbolName] stringByAppendingFormat:@" (%d)", [self count]];
}
@end
    // Old way didn't work:

    // Hmmm... what I really want is a dict and the left column to contain the keys to the dict,
    // and the value is a count.  Can I trust a table view to read a dict?
    // What if I made an array by binding to glyphArray.idName.  Not really necessary: I could
    // already make a table with an array built from glyph.idName.  I need to make an array with
    // only one of each string. (symbolArrayController)  So, back to the dict idea.  I should be
    // able to bind the table content to the dict key and another column to the count.  I'd rather
    // put the count in brackets.  Add that to the todo list and do it with two columns.  No,
    // that's debt.  Just build an array of strings that is what I want.
    /*console.log([symbolArrayController contentArray]);
    console.log([symbolArrayController contentArray][0]);
    console.log([symbolArrayController contentArray][1]);
    console.log(symbolCounts);
    console.log([symbolCounts valueForKey:@"clef.c"]);*/
    // Now append (n) to the end of each string...
    /*var j = 0,
        symbolArray = [symbolArrayController contentArray],
        symbolCount = [symbolArray count];
    for (; j < symbolCount; ++j)
    {
        symbolArray[j] = [symbolArray[j] stringByAppendingFormat:@" (%d)", [symbolCounts objectForKey:symbolArray[j]]];
    }*/
