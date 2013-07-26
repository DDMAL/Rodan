@import <Ratatosk/WLRemoteObject.j>

@import "../Transformers/GlyphsTransformer.j"
@import "Glyph.j"
@import "SymbolCollection.j"

/*
    Parent to Classifier and PageGlyphs
    Note that the GlyphsTableView uses polymorphism - it uses an object
    of type GameraGlyphs which can turn out to be a Classifier or PageGlyphs.)
*/

@implementation GameraGlyphs : WLRemoteObject
{
    CPString           pk                                 @accessors;
    CPArray            glyphs                             @accessors;
    CPArray            symbolCollections                  @accessors;
    CPArrayController  symbolCollectionsArrayController   @accessors;
    CPString           _observingContext;
}

+ (CPArray)remoteProperties
{
    var remoteProperties = [[CPMutableArray alloc] init];

    [remoteProperties addObjectsFromArray:[
        ['pk',     'url'],
        ['glyphs', 'glyphs', [[GlyphsTransformer alloc] init], true]  // true... I think means it's reversible
        ]];

    return remoteProperties;
}

- (id)init
{
    if (self = [super init])
    {
        _observingContext = @"glyphWrite";
        symbolCollectionsArrayController = [[CPArrayController alloc] init];
    }

    return self;
}

- (id)initWithJson:(id)jsonGameraGlyphs
{
    [WLRemoteObject setDirtProof:YES];

    if (self = [super initWithJson:jsonGameraGlyphs])
    {
        [WLRemoteObject setDirtProof:NO];

        var i = 0,
            glyphs_count = [glyphs count],
            prevGlyphName = nil,
            symbolCollectionArray = [[CPMutableArray alloc] init],
            symbolCollection = nil;

        for (i = 0; i < glyphs_count; ++i)
        {
            var glyphName = [glyphs[i] idName];
            if (prevGlyphName === nil || prevGlyphName !== glyphName)
            {
                symbolCollection = [[SymbolCollection alloc] init];
                [symbolCollection setSymbolName:glyphName];
                [symbolCollectionArray addObject:symbolCollection];
            }
            [glyphs[i] addObserver:self forKeyPath:@"idName" options:nil context:_observingContext];
            [symbolCollection addGlyph:glyphs[i]];
            prevGlyphName = glyphName;
        }
        [self setSymbolCollections:symbolCollectionArray];
        [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
    }

    return self;

}

- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(id)aGlyph change:(CPDictionary)aChange context:(id)aContext
{
    if (aContext !== _observingContext)
    {
        console.log("Ratatosk observed a change:");
        console.log(aChange);
        [super observeValueForKeyPath:aKeyPath ofObject:aGlyph change:aChange context:aContext];
    }
    else
    {
        console.log("GameraGlyphs observered a change to a glyph.");
        var newName = [aChange valueForKey:@"CPKeyValueChangeNewKey"],
            oldName = [aChange valueForKey:@"CPKeyValueChangeOldKey"];

        if (oldName !== newName)
        {
            [self addGlyph:aGlyph withName:newName];
        }

        var index = [self findIndexForSymbolCollectionWithName:oldName];

        console.log("---fix the logic---");
        console.log(index);
        console.log([symbolCollections count]);
        console.log([[symbolCollections[index] glyphList] count]);
        if (index < [symbolCollections count] && [[symbolCollections[index] glyphList] count] <= 1)
        {
            // (Comparing count to '1' not '0' because the symbolCollection gets the observer notification 2nd)
            console.log("GameraGlyphs removing empty symbolCollection.");
            [symbolCollections removeObjectAtIndex:index];
            [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
        }
    }
}

- (id)addGlyph:(Glyph)aGlyph withName:(CPString)newName
{
    var index = [self findIndexForSymbolCollectionWithName:newName];

    if (index === [symbolCollections count] || [symbolCollections[index] symbolName] !== newName)
    {
        var newSymbolCollection = [[SymbolCollection alloc] init];
        [newSymbolCollection setSymbolName:newName];
        [symbolCollections insertObject:newSymbolCollection atIndex:index];
        [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
        var selectedObjects = [[symbolCollections[index] cvArrayController] selectedObjects];
        if (selectedObjects)
            console.log("true");
        else
            console.log("false");
        [[symbolCollections[index] cvArrayController] setSelectedObjects:[aGlyph]];
    }

    var selectedObjects = [[symbolCollections[index] cvArrayController] selectedObjects];
    console.log("***Adding a glyph to the selection.");
    console.log("Old selection: ");
    console.log(selectedObjects);

    [symbolCollections[index] addGlyph:aGlyph];
    console.log("[selectedObjects count]: " + [selectedObjects count]);
    if ([selectedObjects count] === 0)
    {
        selectedObjects = [aGlyph];
    }
    else
    {
        [selectedObjects addObject:aGlyph];
    }
    [[symbolCollections[index] cvArrayController] setSelectedObjects:selectedObjects];
    console.log("New selection: ");
    console.log([[symbolCollections[index] cvArrayController] selectedObjects]);
    console.log("Glyph ID: " + [aGlyph UID]);
    // hmmm... something to do with index... and add/remove order... (remove is LAST)
    // only safe in one case, moving UP by ONE (new bin has same index as removed bin)
    // Also, it must be a NEW bin to have the problem.  Aha... I bet the 'add' doesn't work
    //

    // var index;

    // if (index = [self findIndexForSymbolCollectionWithName:[aGlyph idName]])
    // {
    //     // console.log("---Fix the logic:---");
    //     // console.log(index);
    //     // console.log([symbolCollections count]);
    //     // console.log([symbolCollections[index] symbolName]);
    //     // console.log([aGlyph idName]);
    //     if (index < [symbolCollections count] && [symbolCollections[index] symbolName] === [aGlyph idName])
    //     {
    //         // console.log("GameraGlyphs adding glyph to existing symbolCollection");
    //         [symbolCollections[index] addGlyph:aGlyph];
    //     }
    //     else
    //     {
    //         // console.log("GameraGlyphs making a symbolCollection");
    //         var newSymbolCollection = [[SymbolCollection alloc] init];
    //         [newSymbolCollection setSymbolName:[aGlyph idName]];
    //         // console.log([[[self symbolCollectionsArrayController] contentArray] count]);
    //         [symbolCollections insertObject:newSymbolCollection atIndex:index];
    //         // [[self symbolCollections] insertObject:newSymbolCollection atIndex:index];  // Do it without referencing theGameraGlyphs(?)
    //         // [[self symbolCollectionsArrayController] insertObject:newSymbolCollection atArrangedObjectIndex:index];  // Do it without referencing theGameraGlyphs(?)
    //         // [[self symbolCollectionsArrayController] rearrangeObjects];
    //         // console.log([[[self symbolCollectionsArrayController] contentArray] count]);

    //         [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
    //         // [[self symbolCollectionsArrayController] bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
    //         // [[self symbolCollectionsArrayController] rearrangeObjects];
    //         // console.log([[[self symbolCollectionsArrayController] contentArray] count]);
    //         // console.log([self UID]);
    //         // console.log([[self symbolCollectionsArrayController] UID]);
    //         // console.log([[[self symbolCollectionsArrayController] contentArray] UID]);
    //         // console.log([[self symbolCollectionsArrayController] contentArray]);
    //         [symbolCollections[index] addGlyph:aGlyph];
    //     }
    // }
}

- (int)findIndexForSymbolCollectionWithName:(CPString)aSymbolName
{
    // TODO: it would be wonderful if symbolCollectionsArrayController were a DICTIONARY controller.  The tableViews would still work (with a bit of effort,
    // but they can bind to arrangedObjects...) and then I wouldn't need a loop here.
    console.log("findIndexForSymbolCollectionWithName");

    for (var i = 0; i < [symbolCollections count]; ++i)
    {
        if ([symbolCollections[i] symbolName] >= aSymbolName)
        {
            return i;
        }
    }

    return [symbolCollections count];
}

@end
