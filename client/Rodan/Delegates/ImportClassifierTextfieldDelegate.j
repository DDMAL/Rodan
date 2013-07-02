// The purpose of this object is to show the user "Already Used!" with red text if they
// type a taken name when creating a new classifier.  It is assigned as a
// delegate of the text field and implements controlTextDidChange.

@implementation ImportClassifierTextfieldDelegate : CPObject
{
    @outlet ClassifierController classifierController;
}

- (void)controlTextDidChange:(CPNotification)aNotification
{
    [classifierController updateNameUsedLabelInImportWindow];
}
@end
