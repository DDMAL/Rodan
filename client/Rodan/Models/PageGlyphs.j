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

@end
