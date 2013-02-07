@import <Foundation/CPObject.j>

/* A node object for the outline view */
@implementation TreeNode : CPObject
{
    CPString    name    @accessors;
    CPImage     icon    @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        name = @"New Node";
        icon = nil;
    }
    return self;
}

- (id)initWithName:(CPString)aName
{
    var self = [self init];
    name = aName;
    return self;
}

- (id)initWithName:(CPString)aName icon:(CPImage)anIcon
{
    var self = [self init];
    name = aName;
    icon = anIcon
    return self;
}

+ (TreeNode)nodeDataWithName:(CPString)aName
{
    return [[TreeNode alloc] initWithName:aName];
}

+ (TreeNode)nodeDataWithName:(CPString)aName icon:(CPImage)anIcon
{
    return [[TreeNode alloc] initWithName:aName icon:anIcon];
}

- (CPString)humanName
{
    var splitString = [name componentsSeparatedByString:"."];
    if ([splitString count] > 1)
    {
        var theName = [[splitString lastObject] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        return [theName capitalizedString];
    }
    return name;
}
@end
