@import <AppKit/AppKit.j>

@implementation ServerAdminController : CPObject
{
    @outlet     CPToolbar       theToolbar;
    @outlet     CPWindow        theWindow;
    @outlet     CPView          celeryQueueView;
    @outlet     CPView          userAdminView;
    @outlet     CPView          databaseAdminView;
    @outlet     CPView          projectAdminView;
    @outlet     CPView          jobsAdminView;
}

- (IBAction)switchViews:(id)aSender
{
    CPLog("Switch Views");
    var preferencesContentView = [theWindow contentView];

    switch ([aSender itemIdentifier])
    {
        case @"userServerAdminToolbarButton":
            [preferencesContentView setSubviews:[userAdminView]];
            break;
        case @"celeryServerAdminToolbarButton":
            [preferencesContentView setSubviews:[celeryQueueView]];
            break;
        case @"databaseServerAdminToolbarButton":
            [preferencesContentView setSubviews:[databaseAdminView]];
            break;
        case @"projectsServerAdminToolbarButton":
            [preferencesContentView setSubviews:[projectAdminView]];
            break;
        case @"jobsServerAdminToolbarButton":
            [preferencesContentView setSubviews:[jobsAdminView]];
            break;

    }
}
@end
