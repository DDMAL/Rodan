// This object dynamically shows the user "Already Used!" with red text if they
// type a taken name when creating a new classifier.  It is assigned as a
// delegate of the text field and implements controlTextDidChange.

@implementation NewClassifierTextfieldDelegate : CPObject
{
    @outlet ClassifierController classifierController;
}

- (void)controlTextDidChange:(CPNotification)aNotification
{
    [classifierController updateNameUsedLabel];
}
@end
