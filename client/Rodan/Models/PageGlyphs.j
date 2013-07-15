@import "GameraGlyphs.j"

@implementation PageGlyphs : GameraGlyphs
{

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
        [glyphs makeObjectsPerformSelector:@"setPageGlyphs:" withObject:self];
    }

    return self;
}

@end
