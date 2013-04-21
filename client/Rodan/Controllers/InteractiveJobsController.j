/*
    A stub controller to test interactive jobs
*/
@import <RodanKit/RKCrop.j>


@implementation InteractiveJobsController : CPObject
{
}

- (@action)displayCropWindow:(id)aSender
{
    var cropWindow = [[RKCropWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [cropWindow center];
    [cropWindow makeKeyAndOrderFront:aSender];
}

@end;
