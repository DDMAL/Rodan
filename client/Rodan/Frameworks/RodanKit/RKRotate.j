/*
    This instantiates a rotate "view" that is just a window into the interactive view.
*/
@implementation RKRotate : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKRotate init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/rotate"];  // loads the interactive binarise window from Django.
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
@implementation RKRotateWindow : CPWindow
{
    RKRotate     theRotateView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theRotateView = [[RKRotate alloc] initWithFrame:[[self contentView] bounds]];
        [theRotateView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theRotateView];
    }

    return self;
}

@end
