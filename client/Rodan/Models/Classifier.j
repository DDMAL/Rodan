@import "../Transformers/GlyphTransformer.j"

@implementation Classifier : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    name        @accessors;
    CPArray     glyphs      @accessors;
}
- (id)init:(CPString)aName
{
    if (self = [super init])
    {
        [self setName:aName];
    }
    return self;
}
+ (CPArray)remoteProperties  //Ratatosk
{
    return [
        ['pk',          'url'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}
- (CPString)remotePath  //Ratatosk
{
    if ([self pk])
        return [self pk];
    else
        return @"/classifiers/";
}
@end
