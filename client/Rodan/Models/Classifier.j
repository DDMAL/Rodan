@import "../Transformers/GlyphTransformer.j"

@implementation Classifier : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    project     @accessors;
    CPString    name        @accessors;
    CPArray     glyphs      @accessors;
}
// - (id)init:(CPString)aName
// {
//     if (self = [super init])
//     {
//         [self setName:aName];
//         [self setProject:@"debug"];  // Create is giving 400, maybe this'll help
//         // [self setPk:@"mybuggypk"];
//     }
//     return self;
// }
- (id)initWithName:(CPString)aName andProjectPk:(CPString)aProjectPk
{
    if (self = [self init])
    {
        [self setName:aName];
        [self setProject:aProjectPk];
    }
    return self;
}
+ (CPArray)remoteProperties  //Ratatosk
{
    return [
        ['pk',          'url'],
        ['project',     'project'],
        ['name',        'name',      nil, nil],
        ['glyphs',      'glyphs',    [[GlyphTransformer alloc] init]]
    ];
}
- (CPString)remotePath  //Ratatosk
{
    if ([self pk])
    {
        console.log("Classifier remotePath returning: " + [self pk]);
        return [self pk];
    }
    else
    {
        console.log("Classifier remotePath returning: classifiers");
        return @"/classifiers/";
    }
}
@end
