@import <AppKit/CPWebView.j>

@implementation RKDiva : CPWebView
{
}

- (id)initWithFrame:(CGRect)aFrame
{
    console.log("RKDiva init with frame");
    var self = [super initWithFrame:aFrame];
    if (self)
    {
        [self setFrameLoadDelegate:self];
        [self setMainFrameURL:[[CPBundle bundleForClass:[RKDiva class]] pathForResource:@"diva.html"]];
    }

    return self;
}

- (void)webView:(CPWebView)aWebView didFinishLoadForFrame:(id)aFrame  // I think this is always nil...
{
    var jQ = [self DOMWindow].jQuery;
    jQ('#diva-wrapper').diva({
        enableAutoHeight: true,
        fixedHeightGrid: false,
        iipServerURL: "http://coltrane.music.mcgill.ca/fcgi-bin/iipsrv.fcgi?FIF=/mnt/images/beromunster/",
        divaserveURL: "/diva/data/",
        imageDir: "beromunster",
    });
    var dv = jQ('#diva-wrapper').data('diva');
}

@end
