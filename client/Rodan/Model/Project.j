
@implementation Project : CPObject
{
    CPString    projectName     @accessors;
    CPString    description     @accessors;
    CPString    owner           @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        projectName = @"New Project";
    }
    return self;
}

@end
