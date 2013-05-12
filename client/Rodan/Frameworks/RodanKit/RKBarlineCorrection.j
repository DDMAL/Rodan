/*
    This instantiates a barline correction "view" that is just a window into the interactive view.
*/
@implementation RKBarlineCorrection : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKBarlineCorrection init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:@"/interactive/barlinecorrection"];  // loads the interactive binarise window from Django.
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
@implementation RKBarlineCorrectionWindow : CPWindow
{
    RKBarlineCorrection      theBarlineCorrectionView;
}

- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        theBarlineCorrectionView = [[RKBarlineCorrection alloc] initWithFrame:[[self contentView] bounds]];
        [theBarlineCorrectionView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

        [[self contentView] addSubview:theBarlineCorrectionView];
    }

    return self;
}

@end
