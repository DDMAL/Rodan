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

- (void)addGlyph:(Glyph)aGlyph
{
    [self putGlyph:aGlyph intoSymbolCollection:[aGlyph idName]];
    [aGlyph addObserver:self forKeyPath:@"idName" options:nil context:_observingContext];
    [aGlyph setClassifierPk:[self pk]];
    [aGlyph makeAllDirty];
    [aGlyph ensureSaved];

    return;
}

@end
