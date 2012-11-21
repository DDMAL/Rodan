@import <Foundation/CPObject.j>
@import "RodanAPIController.j"

@implementation ProjectsViewController : CPObject
{

}

- (id)init
{
    [[CPNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(resultCallback:)
                                             name:@"ProjectsFetchedNotification"
                                             object:nil];

    var result = [RodanAPIController initWithRequest:"project" notification:@"ProjectsFetchedNotification"];
    console.log(result);
}

- (void)resultCallback:(CPNotification)aNotification
{
    console.log("Result Callback!");
}

@end
