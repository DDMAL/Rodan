
// Importing any classes used in ClassifierView.xib
@import "../Delegates/SymbolTableDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/NewClassifierTextfieldDelegate.j"  // inside ClassifierController... not necessary.
@import "../Delegates/SymbolOutlineDelegate.j"

@import "../Controllers/ClassifierController.j"


@implementation ClassifierViewController : CPViewController
{
    // This object is the bridge between MainMenu.xib and ClassifierView.xib and holds anything
    // that needs to be accessed by both.

    // From CPViewController it inherits a 'view' which is connected to the view defined in
    //  ClassifierView.xib.  This object is accessed by "File's Owner" in ClassifierView.xib

    @outlet ClassifierController classifierController;
}
- (CPViewController)init
{
    // I'm overwriting init because I want to use the object in InterfaceBuilder AND
    // I want it to be initialized in a certain way.  When the cib instantiates
    // ClassifierViewController, it will call this init function
    return [super initWithCibName:@"classifierView" bundle:[CPBundle mainBundle]];
}
- (@action)new:(CPMenuItem)aSender
{
    [classifierController new:aSender];
}
- (@action)open:(CPMenuItem)aSender
{
    [classifierController open:aSender];
}
- (@action)close:(CPMenuItem)aSender
{
    [classifierController close:aSender];
}
@end
