@import "GameraGlyphs.j"

/*
    The real classifier:
    - Inherits from GameraGlyphs, which gives it 'glyphs' and 'symbolCollections'
    - Initialized with a GET to /classifier/uuid
*/
@implementation Classifier : GameraGlyphs
{
    CPString   project   @accessors;
    CPString   name      @accessors;
}

+ (CPArray)remoteProperties
{
    var remoteProperties = [super remoteProperties];
    [remoteProperties addObjectsFromArray:[
        ['project',   'project'],
        ['name',      'name']
    ]];
    return remoteProperties;
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk];
    else
        return @"/classifiers/";
}

- (id)initWithJson:(id)jsonGameraGlyphs
{
    if (self = [super initWithJson:jsonGameraGlyphs])
    {
        [WLRemoteObject setDirtProof:YES];
        [glyphs makeObjectsPerformSelector:@"setClassifierPk:" withObject:[self pk]];
        [WLRemoteObject setDirtProof:NO];
    }

    return self;
}

- (id)addGlyph:(id)aGlyph withName:(CPString)newName
{
    [super addGlyph:aGlyph withName:newName];
    [aGlyph setClassifierPk:[self pk]];
    [aGlyph ensureCreated];

    // var index;

    // if (index = [self findSymbolCollectionWithName:[aGlyph idName]] && ! [[[self symbolCollections] objectAtIndex:index] containsObject:aGlyph])
    // {
    //     // Hmmm, could save some computations by simply checking classifierPk of the glyph instead of actually looking for it.
    //     [[[self symbolCollections] objectAtIndex:index] addGlyph:aGlyph];
    // }
    // else
    // {
    //     var newSymbolCollection = [[SymbolCollection alloc] init];
    //     [newSymbolCollection setSymbolName:newName];
    //     [symbolCollections insertObject:newSymbolCollection atIndex:newBinIndex];  // Do it without referencing theGameraGlyphs(?)
    //     [symbolCollectionArrayController bind:@"content" toObject:theGameraGlyphs withKeyPath:@"symbolCollections" options:nil];  // doesn't actually need to be bound yet

    // }
}

@end
