@implementation OpenClassifierTableViewDelegate : CPObject
{
    @outlet CPWindow deleteClassifierWindow;
}

- (void)tableViewSelectionDidChange:(CPNotification)aNotification
{
    /* Checks if the user opened an 'are you sure' window, and if so,
    that window should keep focus and the current table view should
    not allow the user to change the selection.  It's pretty simple.
    The user hit 'delete,' and shouldn't be able to change the selection
    while the 'are you sure' window is open.
    Correction:  I can't figure out how to make the window keep focus,
    so I just close it.*/
    if ([deleteClassifierWindow isVisible])
    {
        [deleteClassifierWindow close];
    }
}
@end
