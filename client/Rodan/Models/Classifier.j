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
    console.log("[theClassifier addGlyph]");

    [self putGlyph:aGlyph intoSymbolCollection:[aGlyph idName]];
    [aGlyph addObserver:self forKeyPath:@"idName" options:nil context:_observingContext];

    return;

    // TODO: Implement server side API to add the glyph to the classifier.

    [WLRemoteObject setDirtProof:YES];

    [aGlyph setClassifierPk:[self pk]];  // must be done after the glyph gets Patched.
    [aGlyph setEnablePost:YES];
    [aGlyph ensureCreated];  // Gweh, it's not POSTing.  Ratatosk must need pk to be unset.  Arrgghg.
                             // Well, how I about I unset pk and post to /glyphs.
    [aGlyph setEnablePost:NO];

    [WLRemoteObject setDirtProof:NO];


    console.log("____theClassifier addGlyph:withName: finished!!!")

}

@end
