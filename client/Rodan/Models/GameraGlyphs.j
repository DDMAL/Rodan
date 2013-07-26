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
            prevGlyphName = nil,
            symbolCollectionArray = [[CPMutableArray alloc] init],
            symbolCollection = nil;

        for (i = 0; i < [glyphs count]; ++i)
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
        console.log("GameraGlyphs (" + [self class] + ") observered a change to a the idName of a glyph.");

        var newName = [aChange valueForKey:@"CPKeyValueChangeNewKey"],
            oldName = [aChange valueForKey:@"CPKeyValueChangeOldKey"];

        if (oldName !== newName)
        {
            [self putGlyph:aGlyph intoSymbolCollection:newName];

            // [self removeGlyph:aGlyph fromSymbolCollection:oldName];

            var index = [self findIndexForSymbolCollectionWithName:oldName];

            if (index < [symbolCollections count] && (
                    [[symbolCollections[index] glyphList] containsObject:aGlyph] ?
                        [[symbolCollections[index] glyphList] count] <= 1 : [[symbolCollections[index] glyphList] count] <= 0
               ))
            {
                // Hacking out this comparison... With the observer pattern we have no clue whether or not the symbolCollection has
                // removed the glyph yet, and we must remove the symbolCollection if it is emptied by the current operation.  So, the logic
                // is, if the old symbol collection still has the glyph, its count must be 1, and if it doesn't, 0.  (Requesting code review...)
                    // [[symbolCollections[index] glyphList] containsObject:aGlyph] && [[symbolCollections[index] glyphList] count] <= 1 ||
                    // ! [[symbolCollections[index] glyphList] containsObject:aGlyph] && [[symbolCollections[index] glyphList] count] <= 0

                [symbolCollections removeObjectAtIndex:index];
                [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
            }
        }
    }
}

- (id)putGlyph:(Glyph)aGlyph intoSymbolCollection:(CPString)newName
{
    console.log("<GameraGlyphs putGlyph:intoSymbolCollection:>");
    var index = [self findIndexForSymbolCollectionWithName:newName];

    if (index === [symbolCollections count] || [symbolCollections[index] symbolName] !== newName)
    {
        var newSymbolCollection = [[SymbolCollection alloc] init];
        [newSymbolCollection setSymbolName:newName];
        [symbolCollections insertObject:newSymbolCollection atIndex:index];
        [symbolCollectionsArrayController bind:@"content" toObject:self withKeyPath:@"symbolCollections" options:nil];
    }

    var selectedObjects = [[symbolCollections[index] cvArrayController] selectedObjects];
    [symbolCollections[index] addGlyph:aGlyph];
    [selectedObjects addObject:aGlyph];
    [[symbolCollections[index] cvArrayController] setSelectedObjects:selectedObjects];
    console.log("</GameraGlyphs putGlyph:intoSymbolCollection:>");
}

- (int)findIndexForSymbolCollectionWithName:(CPString)aSymbolName
{
    // TODO: it would be wonderful if symbolCollectionsArrayController were a DICTIONARY controller.  The tableViews would still work (with a bit of effort,
    // but they can bind to arrangedObjects...) and then I wouldn't need a loop here.

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
