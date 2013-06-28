
// Importing any classes used in ClassifierView.xib
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/NewClassifierTextfieldDelegate.j"
@import "../Delegates/SymbolOutlineDelegate.j"

@import "../Controllers/ClassifierController.j"

@global RodanShouldLoadClassifierNotification
@global RodanHasFocusClassifierViewNotification

@implementation ClassifierViewController : CPViewController
{
    // This object is the bridge between MainMenu.xib and ClassifierView.xib and holds anything
    // that needs to be accessed by both.  It passes information in code from other Rodan objects
    // to the ClassifierController.

    // From CPViewController it inherits a 'view' which is connected to the view defined in
    //  ClassifierView.xib.  This object is accessed by "File's Owner" in ClassifierView.xib

    @outlet ClassifierController classifierController;
    RunJob runJob @accessors;

}

- (void)awakeFromCib
{
    // Note: This will be called twice.  Once when MainMenu.xib loads, and secondly
    // when ClassifierView.xib loads.

    if (classifierController !== null)
    {
        // This is true for the awakeFromCib called after ClassifierView.xib was loaded
        [[CPNotificationCenter defaultCenter] addObserver:self
                                              selector:@selector(loadRunJob)
                                              name:RodanHasFocusClassifierViewNotification
                                              object:nil];
    }
}

- (CPViewController)init
{
    // I'm overwriting init because I want to use the object in InterfaceBuilder AND
    // I want it to be initialized using initWithCibName.  When the cib instantiates
    // ClassifierViewController, it will call this init function
    self = [super initWithCibName:@"classifierView" bundle:[CPBundle mainBundle]];

    return self;
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

- (@action)finishJob:(CPMenuItem)aSender
{
    [classifierController finishJob:aSender];
}

- (void)workRunJob:(RunJob)aRunJob  // Called by InteractiveJobs controller
{
    runJob = aRunJob;
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadClassifierNotification
                                          object:nil];
}

- (void)loadRunJob  // Called by RodanHasFocusClassifierViewNotification, which is posted AppController after ClassifierView.xib is loaded
{
    if (runJob && classifierController)
    {
        [classifierController loadRunJob:runJob];
    }
}

- (void)fetchClassifiers
{
    [classifierController fetchClassifiers];
}

- (CPArray)getClassifierArrayController
{
    return [classifierController classifierArrayController];
}

@end
