@import <Ratatosk/WLRemoteObject.j>

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
