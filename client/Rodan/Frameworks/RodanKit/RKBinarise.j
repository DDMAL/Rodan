/*
    This instantiates a binarise "view" that is just a window into the interactive view.
*/
@implementation RKBinarise : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKBinarise init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/binarise"];  // loads the interactive binarise window from Django.
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
@implementation RKBinariseWindow : CPWindow
{
    RKBinarise      theBinariseView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theBinariseView = [[RKBinarise alloc] initWithFrame:[[self contentView] bounds]];
        [theBinariseView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theBinariseView];
    }

    return self;
}

@end
