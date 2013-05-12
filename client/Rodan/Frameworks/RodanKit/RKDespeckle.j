/*
    This instantiates a despeckle "view" that is just a window into the interactive view.
*/
@implementation RKDespeckle : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKDespeckle init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/despeckle"];  // loads the interactive binarise window from Django.
    }

    return self;
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
    A window that holds a binarise view.
*/
@implementation RKDespeckleWindow : CPWindow
{
    RKDespeckle      theDespeckleView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theDespeckleView = [[RKDespeckle alloc] initWithFrame:[[self contentView] bounds]];
        [theDespeckleView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theDespeckleView];
    }

    return self;
}

@end
