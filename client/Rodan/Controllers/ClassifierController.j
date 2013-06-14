@import "../Models/Classifier.j"
@import "../Models/Symbol.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/SymbolTableDelegate.j"
@import "../Views/PhotoView.j"  // For the saved collection view

@global activeProject

@implementation ClassifierController : CPObject
{
    Classifier theClassifier;  // Initialized by Open
    @outlet CPArrayController classifierArrayController;

    @outlet CPWindow newClassifierWindow;
    InitNewFetchClassifiersDelegate initNewFetchClassifiersDelegate;
    @outlet NewClassifierTextfieldDelegate newClassifierTextfieldDelegate;
    @outlet CPButton createButton;
    @outlet CPTextField newClassifierTextfield;
    @outlet CPTextField nameUsedLabel;
    @outlet CPWindow openClassifierWindow;
    InitOpenFetchClassifiersDelegate initOpenFetchClassifiersDelegate;
    @outlet CPButton openButton;
    @outlet CPWindow deleteClassifierWindow;
    @outlet CPTableView openClassifierTableView;
    @outlet OpenClassifierTableViewDelegate openClassifierTableViewDelegate;

    @outlet CPArrayController classifierGlyphArrayController;

    @outlet SymbolTableDelegate symbolTableDelegate;

    @outlet ClassifierTableViewDelegate classifierTableViewDelegate;
    @outlet CPTableView classifierTableView;
}
- (void)awakeFromCib
{
    [newClassifierTextfield setDelegate:newClassifierTextfieldDelegate];
        // (Required for red warning text if user enters a classifier name that's already used.)
    [newClassifierWindow setDefaultButton:createButton];
    [openClassifierWindow setDefaultButton:openButton];
    [openClassifierTableView setDelegate:openClassifierTableViewDelegate];
    [classifierTableView setDelegate:classifierTableViewDelegate];
    [classifierTableView setDataSource:classifierTableViewDelegate];

    // Allocating delegates here as to remove clutter from XCode with delegates that do very little.
    initNewFetchClassifiersDelegate  = [[InitNewFetchClassifiersDelegate alloc] init:self];
    initOpenFetchClassifiersDelegate = [[InitOpenFetchClassifiersDelegate alloc] init:self];
}

- (@action)new:(CPMenuItem)aSender
{
    // TODO: consider displaying the classifier list in the New window.
    // (It might help the user to choose a name.)
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifiers/'
                    delegate:initNewFetchClassifiersDelegate
                    message:"Loading classifier list"];
}
- (void)initNewFetchClassifiersDidFinish:(WLRemoteAction)anAction
{
    var classifiers = [Classifier objectsFromJson:[anAction result]];
    [classifierArrayController setContent:classifiers];
    [newClassifierTextfield setStringValue:[self suggestNameForNewClassifier]];
    [self updateNameUsedLabel];
    [newClassifierWindow makeKeyAndOrderFront:null];
}
- (CPString)suggestNameForNewClassifier
// Comes up with a suggestion for the user to name the new classifier.
// Default suggestion is classifier0.
// Expects classifierArrayController to have been populated.
{
    var i = 0,
        classifierCount = [[classifierArrayController contentArray] count];
    for (; i < classifierCount; ++i)
    {
        var suggestion = [[CPString alloc] initWithFormat:@"classifier%d", i];
        if (! [self classifierExists:suggestion])
        {
            return suggestion;
        }
    }
    return @"classifier" + classifierCount.toString();
}
- (Boolean)classifierExists:(CPString)classifierName
/* Tells you if we have a classifier with the given name.
Doesn't go to the server... it relies on the previous call to fetchClassifiers.
Called by the newWindow when choosing a default name, or checking when create
was pressed.*/
{
    //return [self arrayContains:[classifierArrayController contentArray] :classifierName];
    var i = 0,
        classifierArray = [classifierArrayController contentArray],
        classifierCount = [classifierArray count];
    for (; i < classifierCount; ++i)
    {
        if (classifierName === [classifierArray[i] name])
        {
            return true;
        }
    }
    return false;
}
- (void)updateNameUsedLabel
// Gets called on every keystroke of the NewClassifier textbox
{
    if ([self classifierExists:[newClassifierTextfield stringValue]])
    {
        [nameUsedLabel setHidden:NO];
    }
    else
    {
        [nameUsedLabel setHidden:YES];
    }
}
- (@action)createClassifier:(id)aSender
{
    // This is for the create button in the New Classifier window.
    // Check the user's classifier name then create.
    // TODO: Enter button from the textbox must call this function
    var newName = [newClassifierTextfield stringValue];
    if (newName !== @"" && ! [self classifierExists:newName])
    {
        var classifier = [[Classifier alloc] initWithName:newName andProjectPk:[activeProject pk]];
        [classifierArrayController addObject:classifier];
        [classifier ensureCreated];
        [newClassifierWindow close];
    }
    else
    {
        // Do nothing!
        // The user will understand why the button did nothing because of the
        // red text that displays when classifierExists is true.
    }
}
- (@action)open:(CPMenuItem)aSender
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifiers/'
                    delegate:initOpenFetchClassifiersDelegate
                    message:"Loading classifier list for open"];
}
- (void)initOpenFetchClassifiersDidFinish:(WLRemoteAction)anAction
{
    var classifiers = [Classifier objectsFromJson:[anAction result]];
    [classifierArrayController setContent:classifiers];
    [openClassifierWindow makeKeyAndOrderFront:null];  // Opens the window
}
- (@action)openClassifier:(CPButton)aSender
{
    // Read what is selected and get the glyphs of the corresponding classifier.
    var openClassifier = [[classifierArrayController selectedObjects] objectAtIndex:0];
    [openClassifierWindow close];

    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[openClassifier pk]
                    delegate:self
                    message:@"loading a single classifier"];
    // TODO: make this function available by double clicking in the open window
}
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
/* Open operation just finished: server sent us a full classifier */
{
    theClassifier = [[Classifier alloc] initWithJson:[anAction result]];

    console.log("THE CLASSIFIER!");
    console.log(theClassifier);

    [classifierGlyphArrayController bind:@"contentArray"
                                    toObject:theClassifier
                                    withKeyPath:@"glyphs"
                                    options:nil];
    [classifierGlyphArrayController setSortDescriptors:[[CPArray alloc] initWithObjects:[[CPSortDescriptor alloc] initWithKey:@"idName" ascending:YES]]];

    // I'm not sure that the classifierGlyphArrayController gets used at all, as I
    // don't have a view for which there is one view per glyph.
    // [classifierTableViewDelegate initializeTableView:theClassifier];
    [classifierTableViewDelegate initializeTableView:classifierGlyphArrayController];

    [symbolTableDelegate initializeSymbols:theClassifier];
}
- (@action)showAreYouSureWindow:(CPButton)firstDeleteButton
{
    [deleteClassifierWindow makeKeyAndOrderFront:null];
}
- (@action)deleteClassifier:(CPButton)secondDeleteButton
{
    var selectedClassifier = [classifierArrayController selectedObjects];
    [classifierArrayController removeObjects:selectedClassifier];
    [selectedClassifier makeObjectsPerformSelector:@selector(ensureDeleted)];
    [deleteClassifierWindow close];
}
- (@action)writeSymbolName:(CPTextField)aSender
/* Write the new symbol for each selected glyph */
{
    // var newName = [aSender stringValue],
    //     selectedObjects = [classifierGlyphArrayController selectedObjects];
    // for (var i = 0; i < [selectedObjects count]; ++i)
    // {
    //     [selectedObjects[i] writeSymbolName:newName];
    // }
    // [theClassifier makeAllDirty];
    // //[theClassifier makeDirtyProperty:@"id_name"];
    // [theClassifier ensureSaved];

    console.log(theClassifier);
    console.log([[theClassifier glyphs][0] UID]);

    [classifierTableViewDelegate writeSymbolName:[aSender stringValue]];  // This will change the model

    // Also update the symbolTable
    [symbolTableDelegate initializeSymbols:theClassifier];
    // I think this algorithm also works if the user used the symbol table to select, because that will affect the selection of the classifierTable.
    // [symbolTableDelegate writeSymbolName:[aSender stringValue]];  // Shouldn't be needed at all.

    [classifierGlyphArrayController rearrangeObjects];  // Hmm... probably a good idea since some writes happened.
    console.log("Hmmm...");
    [theClassifier makeAllDirty];
    //[theClassifier makeDirtyProperty:@"id_name"];
    [theClassifier ensureSaved];
    // TODO: instead of writing the entire classifier, try doing little patches.
    console.log("Saved classifier.");
    console.log(theClassifier);  // Same classifier as above... the indices change elsewhere...
    console.log([[theClassifier glyphs][0] UID]);
}

- (@action)close:(CPMenuItem)aSender
{
    if (theClassifier)
    {
        if ([theClassifier isDirty])
        {
            [theClassifier ensureSaved];
        }
        theClassifier = null;

        [classifierGlyphArrayController setContent:[]];
        [symbolTableDelegate close];
        [classifierTableViewDelegate close];
    }
}
- (@action)printTheClassifier:(CPButton)aSender  // For debugging
{
    console.log([[theClassifier glyphs][0] UID]);
}

// - (void)fetchClassifiers
// // Fetches classifiers and assigns them to classifierArrayController's content.
// // NOTE: No longer used!
// // I am opting for more controlled versions of this functionality.
// // When I do a fetch, generally want control of the callback.
// // Another way might be to post a notification.
// {
//     [WLRemoteAction schedule:WLRemoteActionGetType
//                     path:'/classifiers/'
//                     delegate:loadClassifiersDelegate  // would just call fetchClassifiersDidFinish
//                     message:"Loading classifier list for new"];
// }
// - (void)fetchClassifiersDidFinish:(WLRemoteAction)anAction
// {
//     var classifiers = [Classifier objectsFromJson:[anAction result]];
//     [classifierArrayController setContent:classifiers];
//         // I get a warning for the previous line, not sure why...
//         // ends up in CPURLConnection.j
// }

@end


@implementation InitNewFetchClassifiersDelegate : CPObject
{
    ClassifierController classifierController;
}
- (id)init:(ClassifierController)aClassifierController
{
    self = [super init];
    classifierController = aClassifierController;
    return self;
}
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController initNewFetchClassifiersDidFinish:anAction];
}
@end

@implementation InitOpenFetchClassifiersDelegate : CPObject
{
    ClassifierController classifierController;
}
- (id)init:(ClassifierController)aClassifierController
{
    self = [super init];
    classifierController = aClassifierController;
    return self;
}
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController initOpenFetchClassifiersDidFinish:anAction];
}
@end

