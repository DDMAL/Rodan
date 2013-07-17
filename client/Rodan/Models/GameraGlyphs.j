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
    CPString        pk                 @accessors;  //remote
    CPArray         glyphs             @accessors;  //remote
    CPMutableArray  symbolCollections  @accessors;  //not remote, but will get clobbered if we do an update
    CPString        _observingContext;
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
            [symbolCollection addGlyph:glyphs[i]];
            [glyphs[i] addObserver:symbolCollection forKeyPath:@"idName" options:nil context:_observingContext];
            [glyphs[i] addObserver:self forKeyPath:@"idName" options:nil context:_observingContext];
            prevGlyphName = glyphName;
        }
        [self setSymbolCollections:symbolCollectionArray];
    }

    return self;

    // COMMENTED: Classless symbolCollection... I want to try this later (see if I can get collectionViews to look at a JSObject, not a classed symbolCollection)
    // [WLRemoteObject setDirtProof:YES];

    // if (self = [super initWithJson:jsonGameraGlyphs])
    // {
    //     [WLRemoteObject setDirtProof:NO];
    //     // Commenting: For now, just get stuff working with the old symbolCollections.
    //     // Later, change it to an 'Object' and see if you can get the collection views to work.
    //     // (We need something working.)

    //     // Note: [super initWithJson] assigns all remote properties that came in from the server .
    //     // We must initialize symbolCollections here

    //     var i = 0,
    //         glyphsCount = [glyphs count],
    //         newSymbolCollections = [[CPMutableDictionary alloc] init],
    //         prevGlyphName = nil;

    //     for (i = 0; i < glyphsCount; ++i)
    //     {
    //         var glyphName = [glyphs[i] idName];
    //         // if ([newSymbolCollections containsKey:glyphName])  // slower alternative
    //         if (prevGlyphName === nil || prevGlyphName !== glyphName)
    //         {
    //             // TODO: We could potentially optimize this by assuming alphabetical order.
    //             // (containsKey might be a bit slow.)  prevGlyph...
    //             // We could even write this generically, so that it doesn't clobber symbolCollections
    //             // if Ratatosk does an update... we lose guaranteed syncing but maybe that's okay (since
    //             // the client is doing the talking.)
    //             var newGlyphList = [[CPMutableArray alloc] init];
    //             [newSymbolCollections setObject:newGlyphList forKey:glyphName];
    //         }
    //         [[newSymbolCollections objectForKey:glyphName] addObject:glyphs[i]];
    //         [glyphs[i] addObserver:self forKeyPath:@"idName" options:nil context:nil];
    //         prevGlyphName = glyphName;
    //     }

    //     [self setSymbolCollections:newSymbolCollections];
    //     console.log("newSymbolCollections");
    //     console.log(newSymbolCollections);
    // }

    // return self;
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
        console.log(aChange);
    }
}

- (CPDictionary)makeSymbolCollections
{
    return nil;
}

@end
