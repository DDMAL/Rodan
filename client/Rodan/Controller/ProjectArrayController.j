@import <AppKit/AppKit.j>

@implementation ProjectArrayController : CPArrayController
{

}

- (id)init
{
    if (self = [super init])
    {

    }
    return self;
}

- (IBAction)add:(id)aSender
{
    [super add:aSender];
    console.log([self contentArray]);
}


@end
