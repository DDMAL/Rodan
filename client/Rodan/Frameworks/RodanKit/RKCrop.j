

/*
    This instantiates a crop "view" that is just a window into the interactive view.
*/
@implementation RKCrop : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKCrop init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/crop"];  // loads the interactive crop window from Django.
    }

    return self;
}

- (CPArray)cropArea
{
    var domWin = [self DOMWindow];

    // unimplemented. When implemented it should query the frame via the DOM window
    // and return the crop area in an array of points.

    return [[CPArray alloc] init];
}

#pragma mark -
#pragma mark Delegate method for web view

- (void)webView:(CPWebView)aWebView didFinishLoadForFrame:(id)aFrame
{
    var bounds = [self bounds],
        domWin = [self DOMWindow];

    console.log("Did finish loading delegate");
}

@end

/*
    A window that holds a crop view.
*/
@implementation RKCropWindow : CPWindow
{
    RKCrop      theCropView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theCropView = [[RKCrop alloc] initWithFrame:[[self contentView] bounds]];
        [theCropView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theCropView];
    }

    return self;
}

@end
