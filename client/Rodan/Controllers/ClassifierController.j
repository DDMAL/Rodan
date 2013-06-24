@import "../Models/Classifier.j"
@import "../Models/PageGlyphs.j"
@import "../Models/Symbol.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/PageGlyphsTableViewDelegate.j"
@import "../Delegates/SymbolTableDelegate.j"
@import "../Delegates/ClassifierControllerFetchDelegates.j"

@global activeProject

@implementation ClassifierController : CPObject
{
    Classifier theClassifier;
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

    @outlet ClassifierTableViewDelegate classifierTableViewDelegate;
    @outlet PageGlyphsTableViewDelegate pageGlyphsTableViewDelegate;
    @outlet CPArrayController classifierSymbolCollectionArrayController;
    @outlet CPArrayController pageGlyphsSymbolCollectionArrayController;

    PageGlyphs thePageGlyphs;
    FetchPageGlyphsDelegate fetchPageGlyphsDelegate;

    @outlet SymbolTableDelegate symbolTableDelegate;
}

- (void)awakeFromCib
{
    [newClassifierTextfield setDelegate:newClassifierTextfieldDelegate];

    [newClassifierWindow setDefaultButton:createButton];
    [openClassifierWindow setDefaultButton:openButton];
    [openClassifierTableView setDelegate:openClassifierTableViewDelegate];

    // Allocating delegates here as to remove clutter from XCode with delegates that do very little.
    initNewFetchClassifiersDelegate  = [[InitNewFetchClassifiersDelegate alloc] initWithClassifierController:self];
    initOpenFetchClassifiersDelegate = [[InitOpenFetchClassifiersDelegate alloc] initWithClassifierController:self];
    fetchPageGlyphsDelegate = [[FetchPageGlyphsDelegate alloc] initWithClassifierController:self];
}

- (void)loadRunJob:(RunJob)aRunJob
{
    [self fetchClassifier:[[aRunJob jobSettings] objectForKey:@"classifier"]];
    [self fetchPageGlyphs:[[aRunJob jobSettings] objectForKey:@"pageglyphs"]];
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
    console.log("fetchPageGlyphsDidFinish");
    thePageGlyphs = [[PageGlyphs alloc] initWithJson:[anAction result]];
    [pageGlyphsTableViewDelegate setTheGameraGlyphs:thePageGlyphs];
    [pageGlyphsSymbolCollectionArrayController bind:@"content" toObject:thePageGlyphs withKeyPath:@"symbolCollections" options:nil];
    [pageGlyphsTableViewDelegate initializeTableView];
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

    [classifierTableViewDelegate setTheGameraGlyphs:theClassifier];

    [classifierSymbolCollectionArrayController bind:@"content" toObject:theClassifier withKeyPath:@"symbolCollections" options:nil];
    [classifierTableViewDelegate initializeTableView];

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
    // TODO: This should be disabled if we don't have a classifier loaded.
    [classifierTableViewDelegate writeSymbolName:[aSender stringValue]];
    [pageGlyphsTableViewDelegate writeSymbolName:[aSender stringValue]];

    // [symbolTableDelegate initializeSymbols:theClassifier];  // Broke by new model

    // [symbolTableDelegate writeSymbolName:[aSender stringValue]];  // Shouldn't be needed at all.

    [theClassifier makeAllDirty];
    //[theClassifier makeDirtyProperty:@"id_name"];
    [theClassifier ensureSaved];
    // TODO: instead of writing the entire classifier, try to send less JSON and just patch a bit.

    [thePageGlyphs makeAllDirty];
    [thePageGlyphs ensureSaved];
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

        [symbolTableDelegate close];
        [classifierTableViewDelegate close];
    }
}

- (@action)printTheClassifier:(CPButton)aSender  // For debugging
{
    console.log([[[theClassifier symbolCollections][0] glyphList][0] UID]);
}
@end

