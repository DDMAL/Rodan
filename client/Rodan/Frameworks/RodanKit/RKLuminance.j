/*
    This instantiates a luminance "view" that is just a window into the interactive view.
*/
@implementation RKLuminance : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKLuminance init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/luminance"];  // loads the interactive binarise window from Django.
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
@implementation RKLuminanceWindow : CPWindow
{
    RKLuminance      theLuminanceView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theLuminanceView = [[RKLuminance alloc] initWithFrame:[[self contentView] bounds]];
        [theLuminanceView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theLuminanceView];
    }

    return self;
}

@end
