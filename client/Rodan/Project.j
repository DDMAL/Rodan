@import <Foundation/CPObject.j>

// The Project Model
@implementation Project : CPObject
{
    CPString projectName @accessors;
    CPString description @accessors;
    CPString resourceURI @accessors;
}

+ (id)projectWithObject:(JSObject)anObject
{
    var project = [[self alloc] init];
    [project setProjectName:anObject.name];
    [project setDescription:anObject.description];
    [project setResourceURI:anObject.resource_uri];

    return project;
}

@end
