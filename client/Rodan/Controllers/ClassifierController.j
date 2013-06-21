@import "../Models/Classifier.j"
@import "../Models/PageGlyphs.j"
@import "../Models/Symbol.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/SymbolTableDelegate.j"
@import "../Delegates/ClassifierControllerFetchDelegates.j"

@global activeProject

@implementation ClassifierController : CPObject
{
    Classifier theClassifier @accessors;  // accessors to help debug ClassifierTableViewDelegate
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

    PageGlyphs thePageGlyphs;
    FetchPageGlyphsDelegate fetchPageGlyphsDelegate;

    @outlet CPArrayController symbolCollectionArrayController;
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
    initNewFetchClassifiersDelegate  = [[InitNewFetchClassifiersDelegate alloc] initWithClassifierController:self];
    initOpenFetchClassifiersDelegate = [[InitOpenFetchClassifiersDelegate alloc] initWithClassifierController:self];
    fetchPageGlyphsDelegate = [[FetchPageGlyphsDelegate alloc] initWithClassifierController:self];
}

- (void)loadRunJob:(RunJob)aRunJob
{
    // [self fetchPageGlyphs:[[aRunJob jobSettings] objectForKey:@"pageglyphs"]];
    [self fetchClassifier:[[aRunJob jobSettings] objectForKey:@"classifier"]];

    // Also get the page image from the runJob
    // [WLRemoteAction schedule:WLRemoteActionGetType
    //                 path:[[aRunJob jobSettings]['pageglyphs'] pk]
    //                 delegate:loadPageGlyphsDelegate
    //                 message:@"loading a single classifier"];  // Maybe I have it already.
}

- (void)fetchClassifier:(CPString)uuid
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifier/' + uuid
                    delegate:self
                    message:@"loading a single classifier"];
}

- (void)fetchPageGlyphs:(CPString)uuid
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/pageglyphs/' + uuid
                    delegate:fetchPageGlyphsDelegate  // forwards to fetchPageGlyphsDidFinish
                    message:@"loading a single classifier"];
}

- (void)fetchPageGlyphsDidFinish:(WLRemoteAction)anAction
{
    thePageGlyphs = [[PageGlyphs alloc] initWithJson:[anAction result]];
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

/*
    Comes up with a suggestion for the user to name the new classifier.
    Default suggestion is classifier0.
    Expects classifierArrayController to have been populated.
*/
- (CPString)suggestNameForNewClassifier
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

/*
    Tells you if we have a classifier with the given name.
    Doesn't go to the server... it relies on the previous call to fetchClassifiers.
    Called by the newWindow when choosing a default name, or checking when create
    was pressed.
*/
- (Boolean)classifierExists:(CPString)classifierName
{
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

/*
    This is for the create button in the New Classifier window.
    Check the user's classifier name then create.
    TODO: Enter button from the textbox must call this function
*/
- (@action)createClassifier:(id)aSender
{
    var newName = [newClassifierTextfield stringValue];
    if (newName !== @"" && ![self classifierExists:newName])
    {
        var classifier = [[Classifier alloc] initWithName:newName andProjectPk:[activeProject pk]];
        [classifierArrayController addObject:classifier];
        [classifier ensureCreated];
        [newClassifierWindow close];
    }
    return nil;
    // Do nothing!
    // The user will understand why the button did nothing because of the
    // red text that displays when classifierExists is true.
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
    [openClassifierWindow makeKeyAndOrderFront:null];
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
{
    // Open operation just finished: server sent us a full classifier

    theClassifier = [[Classifier alloc] initWithJson:[anAction result]];

    console.log("THE CLASSIFIER!");
    console.log(theClassifier);
    [classifierTableViewDelegate setTheClassifier:theClassifier];

    // [classifierGlyphArrayController bind:@"contentArray"
    //                                 toObject:theClassifier
    //                                 withKeyPath:@"glyphs"
    //                                 options:nil];
    // [classifierGlyphArrayController setSortDescriptors:[[CPArray alloc] initWithObjects:[[CPSortDescriptor alloc] initWithKey:@"idName" ascending:YES]]];

    // I'm not sure that the classifierGlyphArrayController gets used at all, as I
    // don't have a view for which there is one view per glyph.
    // [classifierTableViewDelegate initializeTableView:theClassifier];

    // [symbolCollectionArrayController setContent:[theClassifier symbolCollections]];
    [symbolCollectionArrayController bind:@"content" toObject:theClassifier withKeyPath:@"symbolCollections" options:nil];

    [classifierTableViewDelegate initializeTableView];
    [classifierTableView reloadData];  // TODO: initializeTableView should do this... I'm putting it outside to help debug ClassifierTableViewDelegate

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

/*
    Write the new symbol for each selected glyph
*/
- (@action)writeSymbolName:(CPTextField)aSender
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
    console.log([[[theClassifier symbolCollections][0] glyphList][0] UID]);
    [classifierTableViewDelegate writeSymbolName:[aSender stringValue]];  // This will change the model
        // Ok.  Are the selected objects the same objects that are in the model?
    // console.log([[theClassifier glyphs][0] UID]);

    // Also update the symbolTable
    // [symbolTableDelegate initializeSymbols:theClassifier];  // Broke by new model

    // I think this algorithm also works if the user used the symbol table to select, because that will affect the selection of the classifierTable.
    // [symbolTableDelegate writeSymbolName:[aSender stringValue]];  // Shouldn't be needed at all.

    // [classifierGlyphArrayController rearrangeObjects];  // Hmm... probably a good idea since some writes happened.
    console.log("Hmmm...");
    [theClassifier makeAllDirty];
    //[theClassifier makeDirtyProperty:@"id_name"];
    [theClassifier ensureSaved];
    // TODO: instead of writing the entire classifier, try doing little patches.
    console.log("Saved classifier.");
    console.log(theClassifier);  // Same classifier as above... the indices change elsewhere...
    // console.log([[theClassifier glyphs][0] UID]);
    // So the classifier indices are changing and not the symbolCollections.  And they don't change on ensureSaved.
    // [symbolCollectionArrayController bind:@"content" toObject:theClassifier withKeyPath:@"symbolCollections" options:nil];
    // [classifierTableViewDelegate initializeTableView];
    // [classifierTableView reloadData];

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
    console.log([[[theClassifier symbolCollections][0] glyphList][0] UID]);
}
@end

