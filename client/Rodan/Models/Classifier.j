@import <Ratatosk/WLRemoteObject.j>

@import "GameraGlyphs.j"

/*
    MinimalClassifier
    - Doesn't have glyphs
    - initialized with a GET to /classifiers/, or on the client and POSTed to /classifiers/
*/

@implementation MinimalClassifier : WLRemoteObject
{
    CPString  pk          @accessors;
    CPString  project     @accessors;
    CPString  name        @accessors;
    CPString  pageglyphs  @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['project', 'project'],
        ['name', 'name'],
        ['pageglyphs', 'pageglyphs']
    ];
}

- (CPString)remotePath
{
    if ([self pk])
        return [self pk];
    else
        return @"/classifiers/";
}

- (id)initWithName:(CPString)aName andProjectPk:(CPString)aProjectPk
{
    if (self = [self init])
    {
        [self setName:aName];
        [self setProject:aProjectPk];
    }
    return self;
}

@end

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

@end
