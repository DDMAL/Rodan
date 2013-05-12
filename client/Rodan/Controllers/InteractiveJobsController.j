/*
    A stub controller to test interactive jobs
*/
@import <RodanKit/RKCrop.j>
@import <RodanKit/RKBinarise.j>
@import <RodanKit/RKDespeckle.j>
@import <RodanKit/RKRotate.j>
@import <RodanKit/RKSegment.j>
@import <RodanKit/RKLuminance.j>
@import <RodanKit/RKBarlineCorrection.j>
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

- (@action)displayBinariseWindow:(id)aSender
{
    var binariseWindow = [[RKBinariseWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [binariseWindow center];
    [binariseWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayDespeckleWindow:(id)aSender
{
    var despeckleWindow = [[RKDespeckleWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [despeckleWindow center];
    [despeckleWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayRotateWindow:(id)aSender
{
    var rotateWindow = [[RKRotateWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [rotateWindow center];
    [rotateWindow makeKeyAndOrderFront:aSender];
}

- (@action)displaySegmentWindow:(id)aSender
{
    var segmentWindow = [[RKSegmentWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [segmentWindow center];
    [segmentWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayLuminanceWindow:(id)aSender
{
    var luminanceWindow = [[RKLuminanceWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [luminanceWindow center];
    [luminanceWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayBarlineCorrectionWindow:(id)aSender
{
    var barlineCorrectionWindow = [[RKBarlineCorrectionWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [barlineCorrectionWindow center];
    [barlineCorrectionWindow makeKeyAndOrderFront:aSender];
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
