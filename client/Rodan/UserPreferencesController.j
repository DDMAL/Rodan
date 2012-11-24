@import <AppKit/AppKit.j>

@implementation UserPreferencesController : CPWindowController
{
    @outlet     CPToolbar       theToolbar;
    @outlet     CPWindow        theWindow;
    @outlet     CPView          accountPreferencesView;
}


- (id)init
{
    CPLog("UserPreferencesController Awake!");
    self = [super initWithWindowCibName:@"Preferences"];

    if (self)
    {
    }

    // var contentView = [theWindow contentView],
    //     bounds = [contentView bounds];

    // console.log(bounds);
    // console.log(theWindow);

    // [contentView addSubview:[accountPreferencesView]];

    CPLog(theWindow);
    return self;
}

- (void)awakeFromCib
{
    CPLog("Awwaaakkeekee!");
}

- (void)windowDidResize:(CPNotification)notification
{
    CPLog("Resize");
}

- (IBAction)switchPreferences:(id)aSender
{
    CPLog("Switch Preferences");
}

- (IBAction)onActivate:(id)aSender
{
    CPLog("Activate!");
}
