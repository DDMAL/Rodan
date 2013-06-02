/**
 * This is a general interactive job view that most (if not all) interactive jobs can use.
 */
@implementation RKInteractiveJob : CPWebView
{
}


- (id)initWithFrame:(CGRect)aFrame runJobUUID:(int)aRunJobUUID jobName:(CPString)aJobName
{
    console.log("RKInteractiveJob init with frame; RunJob UUID is " + aRunJobUUID);
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        var urlPart = [[CPBundle bundleForClass:[self class]] objectForInfoDictionaryKey:aJobName];
        [self setMainFrameURL:@"/interactive/" + urlPart + "?runjob=" + aRunJobUUID];
    }
    return self;
}


- (void)webView:(CPWebView)aWebView didFinishLoadForFrame:(id)aFrame
{
    var bounds = [self bounds],
        domWin = [self DOMWindow];
    console.log("Did finish loading delegate");
}
@end


/**
 * The containing window for the interactive job view.
 */
@implementation RKInteractiveJobWindow : CPWindow
{
    RKInteractiveJob      interactiveJob;
}


- (id)initWithContentRect:(CGRect)aRect styleMask:(int)aMask runJobUUID:(int)aRunJobUUID jobName:(CPString)aJobName
{
    var self = [super initWithContentRect:aRect styleMask:aMask];
    if (self)
    {
        interactiveJob = [[RKInteractiveJob alloc] initWithFrame:[[self contentView] bounds] runJobUUID:aRunJobUUID jobName:aJobName];
        [interactiveJob setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];
        [[self contentView] addSubview:interactiveJob];
    }
    return self;
}
@end
