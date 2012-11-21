@import <Foundation/CPObject.j>
@import "RodanAPIController.j"

@implementation ProjectsViewController : CPObject
{

}

- (id)init
{
    self = [super init];
    if (self)
    {
        [[CPNotificationCenter defaultCenter] addObserver:self
                                                 selector:@selector(resultCallback:)
                                                 name:@"ProjectsFetchedNotification"
                                                 object:nil];

        var result = [RodanAPIController initWithRequest:"project" notification:@"ProjectsFetchedNotification"];
        console.log(result);
    }
    return self;
}

- (void)resultCallback:(CPNotification)aNotification
{
    console.log("Result Callback!");
    console.log([aNotification object]);
}

@end
