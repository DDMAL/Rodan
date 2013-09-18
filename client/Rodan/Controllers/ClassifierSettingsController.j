
@import "UploadWindowController.j"
@import "../Models/ClassifierSetting.j"

@implementation ClassifierSettingsController : CPObject
{
    @outlet UploadWindowController settingsWindowController;
}

- (@action)importSettings:(CPMenuItem)aSender
{
    [settingsWindowController openWindow];
}

@end
