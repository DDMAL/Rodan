/*
    A stub controller to test interactive jobs
*/
@import <RodanKit/RKCrop.j>
@import <RodanKit/RKDiva.j>


@implementation InteractiveJobsController : CPObject
{
}

- (@action)displayCropWindow:(id)aSender
{
    var cropWindow = [[RKCropWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [cropWindow center];
    [cropWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayDivaWindow:(id)aSender
{
    var divaWindow = [[CPWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask],
        divaView = [[RKDiva alloc] initWithFrame:[[divaWindow contentView] bounds]];
    [divaView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

    [[divaWindow contentView] addSubview:divaView];
    [divaWindow center];
    [divaWindow makeKeyAndOrderFront:aSender];
}

@end;
