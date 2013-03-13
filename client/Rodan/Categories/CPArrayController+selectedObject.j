@import <AppKit/CPArrayController.j>

/*
    Adds a simple method to the array controller
    that allows you to get back a single selected object.
*/
@implementation CPArrayController (SelectedObject)
{
}

- (id)selectedObject
{
    return [[self contentArray] objectAtIndex:[self selectionIndex]];
}

@end
