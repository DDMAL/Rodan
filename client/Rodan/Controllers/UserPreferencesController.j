@import <AppKit/AppKit.j>

@implementation UserPreferencesController : CPObject
{
    @outlet     CPToolbar       theToolbar;
    @outlet     CPWindow        theWindow;
    @outlet     CPView          accountPreferencesView;
    @outlet     CPView          somethingElseView;
}


- (IBAction)switchPreferences:(id)aSender
{
    CPLog("Switch Preferences");
    var preferencesContentView = [theWindow contentView];
    switch ([aSender itemIdentifier])
    {
        case @"accountPreferencesToolbarButton":
            [preferencesContentView setSubviews:[accountPreferencesView]];
            break;
        case @"somethingElseToolbarButton":
            [preferencesContentView setSubviews:[somethingElseView]];
            break;
    }
}
@end
