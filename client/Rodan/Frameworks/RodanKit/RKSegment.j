/*
    This instantiates a segment "view" that is just a window into the interactive view.
*/
@implementation RKSegment : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKSegment init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/segment"];  // loads the interactive binarise window from Django.
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
@implementation RKSegmentWindow : CPWindow
{
    RKSegment      theSegmentView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theSegmentView = [[RKSegment alloc] initWithFrame:[[self contentView] bounds]];
        [theSegmentView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theSegmentView];
    }

    return self;
}

@end
