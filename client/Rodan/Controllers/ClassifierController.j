@import "../Models/Classifier.j"
@import "../Models/MinimalClassifier.j"
@import "../Models/PageGlyphs.j"
@import "../Delegates/OpenClassifierTableViewDelegate.j"
@import "../Delegates/ClassifierTableViewDelegate.j"
@import "../Delegates/PageGlyphsTableViewDelegate.j"
@import "../Delegates/ClassifierControllerFetchDelegates.j"

@global activeProject

@implementation ClassifierController : CPObject
{
    Classifier theClassifier;
    @outlet CPArrayController classifierArrayController @accessors;

    FetchClassifiersDelegate fetchClassifiersDelegate;

    @outlet CPWindow newClassifierWindow;
    InitNewFetchClassifiersDelegate initNewFetchClassifiersDelegate;
    @outlet CPButton createButton;
    @outlet CPTextField newClassifierTextfield;
    @outlet CPTextField nameUsedLabel;

    @outlet CPWindow importClassifierWindow;
    InitImportFetchClassifiersDelegate initImportFetchClassifiersDelegate;
    @outlet UploadButton importClassifierChooseFileButton;
    @outlet CPButton importCreateButton;
    @outlet CPTextField importClassifierNameTextfield;
    @outlet CPTextField importClassifierFileTextfield;
    @outlet CPTextField nameUsedLabelInImportWindow;

    @outlet CPWindow openClassifierWindow;
    InitOpenFetchClassifiersDelegate initOpenFetchClassifiersDelegate;
    @outlet CPButton openButton;
    @outlet CPWindow deleteClassifierWindow;
    @outlet CPTableView openClassifierTableView;
    @outlet OpenClassifierTableViewDelegate openClassifierTableViewDelegate;

    @outlet ClassifierTableViewDelegate classifierTableViewDelegate;
    @outlet PageGlyphsTableViewDelegate pageGlyphsTableViewDelegate;

    PageGlyphs thePageGlyphs;
    FetchPageGlyphsDelegate fetchPageGlyphsDelegate;
    FetchClassifiersDelegate fetchClassifiersDelegate;

    @outlet CPObjectController pageImageController;

    Runjob theRunJob;

    @outlet CPTableColumn symbolTableColumn;
}

- (void)awakeFromCib
{
    [newClassifierWindow setDefaultButton:createButton];
    [importClassifierWindow setDefaultButton:importCreateButton];
    [openClassifierWindow setDefaultButton:openButton];
    [openClassifierTableView setDelegate:openClassifierTableViewDelegate];

    // Allocating delegates here to remove clutter from XCode with delegates that do very little.
    fetchClassifiersDelegate  = [[FetchClassifiersDelegate alloc] initWithClassifierController:self];
    initNewFetchClassifiersDelegate  = [[InitNewFetchClassifiersDelegate alloc] initWithClassifierController:self];
    initImportFetchClassifiersDelegate  = [[InitImportFetchClassifiersDelegate alloc] initWithClassifierController:self];
    initOpenFetchClassifiersDelegate = [[InitOpenFetchClassifiersDelegate alloc] initWithClassifierController:self];
    fetchPageGlyphsDelegate = [[FetchPageGlyphsDelegate alloc] initWithClassifierController:self];
}

/*
    new: This menu item creates a new empty classifier by sending a POST request to /classifiers.
*/
- (@action)new:(CPMenuItem)aSender
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifiers/'
                    delegate:initNewFetchClassifiersDelegate
                    message:"Loading classifier list"];
}

- (void)initNewFetchClassifiersDidFinish:(WLRemoteAction)anAction
{
    [self updateClassifierArrayControllerWithResponse:anAction];
    [newClassifierTextfield setStringValue:@""];
    [nameUsedLabel setHidden:YES];
    [newClassifierWindow makeKeyAndOrderFront:null];
}

- (void)updateNameUsedLabel
{
    if ([self classifierExists:[newClassifierTextfield stringValue]])
    {
        [nameUsedLabel setStringValue:@"Name unavailable."];
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
*/
- (@action)createClassifier:(id)aSender
{
    var newName = [newClassifierTextfield stringValue];

    if (newName === @"")
    {
        [nameUsedLabel setStringValue:@"Name cannot be blank."];
        [nameUsedLabel setHidden:NO];
    }
    else if (![self classifierExists:newName])
    {
        var classifier = [[MinimalClassifier alloc] initWithName:newName andProjectPk:[activeProject pk]];
        [classifierArrayController addObject:classifier];
        [classifier ensureCreated];
        [newClassifierWindow close];
    }

    return nil;
}

/*
    classifierExists: Tells you if we have a classifier with the given name.
    Doesn't go to the server... it relies on a previous fetch (like initNewFetchClassifiersDidFinish).
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

/*
    importFromXML: This function opens the "Import From XML..." window which allows the user to
    upload a classifier XML made with Gamera to be used by Rodan.  The window uses an "UploadButton"
    to do the POST that creates the classifier.  The way it works is that fields are set on the
    UploadButton, and then you call 'submit' to execute the POST request.
    The UploadButton is actually the one marked "Choose..." (importClassifierChooseFileButton,) and
    the button marked "Submit" simply sends the 'submit' message to the other button.  The reason for
    this is usability: I wanted the user to choose a file and then submit it in two actions, to give
    them a chance to look at the name and the file together before confirming.
*/

- (@action)importFromXML:(CPMenuItem)aSender
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifiers/'
                    delegate:initImportFetchClassifiersDelegate
                    message:"Loading classifier list"];
}

- (void)initImportFetchClassifiersDidFinish:(WLRemoteAction)anAction
{
    [self updateClassifierArrayControllerWithResponse:anAction];
    [importClassifierNameTextfield setStringValue:@""];
    [importClassifierFileTextfield setStringValue:@""];
    [nameUsedLabelInImportWindow setHidden:YES];
    [importClassifierChooseFileButton resetSelection];
    [importClassifierWindow makeKeyAndOrderFront:null];
}

- (void)updateNameUsedLabelInImportWindow
{
    if ([self classifierExists:[importClassifierNameTextfield stringValue]])
    {
        [nameUsedLabelInImportWindow setStringValue:@"Name unavailable."];
        [nameUsedLabelInImportWindow setHidden:NO];
    }
    else
    {
        [nameUsedLabelInImportWindow setHidden:YES];
    }
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection  // Delegate method for uploading XML
{
    var oldNameFromFile = [self clipFileExtension:[importClassifierFileTextfield stringValue]],
        currentName = [importClassifierNameTextfield stringValue];

    if (currentName === @"" || currentName === oldNameFromFile)
    {
        // Update the Name textfield if it's empty or the user hasn't changed anything
        var newName = [self clipFileExtension:selection];

        [importClassifierNameTextfield setStringValue:newName];
        [self updateNameUsedLabelInImportWindow];
    }

    [importClassifierFileTextfield setStringValue:selection];
}

- (CPString)clipFileExtension:(CPString)fileName
{
    var fileExtensionRe = /^(.+)\..+?$/,
        matchResult = fileExtensionRe.exec(fileName);

    if (matchResult && matchResult[1])
    {
        return matchResult[1];
    }
    else
    {
        return @"";
    }
}

- (@action)uploadClassifier:(CPButton)submitButton
{
    var newName = [importClassifierNameTextfield stringValue];

    if (newName === @"")
    {
        [nameUsedLabelInImportWindow setStringValue:@"Name cannot be blank."];
        [nameUsedLabelInImportWindow setHidden:NO];
    }
    else if ([importClassifierFileTextfield stringValue] === @"")
    {
        [nameUsedLabelInImportWindow setStringValue:@"Choose a file to upload."];
        [nameUsedLabelInImportWindow setHidden:NO];
    }
    else if ([self classifierExists:newName])
    {
        [self updateNameUsedLabelInImportWindow];
    }
    else
    {
        [importClassifierChooseFileButton setValue:[activeProject pk] forParameter:@"project"];
        [importClassifierChooseFileButton setValue:[importClassifierNameTextfield stringValue] forParameter:@"name"];
        [importClassifierChooseFileButton submit];  // Sends a POST to /classifiers/ (see setup in ClassifierViewController's awakeFromCib)
    }
}

- (void)uploadButtonDidBeginUpload:(UploadButton)button  // Delegate method for uploading XML
{
    // This function is called when upload button is pressed.
    // It's not needed because uploadClassifier: does the job.
}

- (void)uploadButton:(UploadButton)button didFailWithError:(CPString)anError  // Delegate method for uploading XML
{
    CPLog.error(anError);
}

- (void)uploadButton:(UploadButton)button didFinishUploadWithData:(CPString)response  // Delegate method for uploading XML
{
    [button resetSelection];
    var data = JSON.parse(response);
    [self createObjectsWithJSONResponse:data];
    [importClassifierWindow close];
}

- (void)createObjectsWithJSONResponse:(id)aResponse
{
    [WLRemoteObject setDirtProof:YES];
    var newClassifiers = [MinimalClassifier objectsFromJson:[aResponse]];
    [classifierArrayController addObjects:newClassifiers];
    [WLRemoteObject setDirtProof:NO];
}

- (void)fetchClassifiers
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:'/classifiers/'
                    delegate:fetchClassifiersDelegate
                    message:"Loading classifier list"];
}

- (void)fetchClassifiersDidFinish:(WLRemoteAction)anAction
{
    [self updateClassifierArrayControllerWithResponse:anAction];
}

- (void)updateClassifierArrayControllerWithResponse:(WLRemoteAction)anAction
{
    var classifiers = [MinimalClassifier objectsFromJson:[anAction result]];
    [classifierArrayController setContent:classifiers];
}

/*
    loadRunJob is called when Rodan has displayed the Classifier interface
    and it's time to get the data using the RunJob settings and populate the
    displays.
*/
- (void)loadRunJob:(RunJob)aRunJob
{
    theRunJob = aRunJob;
    [self fetchClassifier:[[aRunJob jobSettings] objectForKey:@"classifier"]];
    [self fetchPageGlyphs:[[aRunJob jobSettings] objectForKey:@"pageglyphs"]];
    [pageImageController setContent:[aRunJob page]];
}

- (void)fetchClassifier:(CPString)pk
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:pk
                    delegate:self
                    message:@"loading a single classifier"];
}

- (void)fetchPageGlyphs:(CPString)pk
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:pk
                    delegate:fetchPageGlyphsDelegate
                    message:@"loading a single set of page glyphs"];
}

- (void)fetchPageGlyphsDidFinish:(WLRemoteAction)anAction
{
    thePageGlyphs = [[PageGlyphs alloc] initWithJson:[anAction result]];
    [pageGlyphsTableViewDelegate setTheGameraGlyphs:thePageGlyphs];
    // [pageGlyphsSymbolCollectionArrayController bind:@"content" toObject:thePageGlyphs withKeyPath:@"symbolCollections" options:nil];

    [pageGlyphsTableViewDelegate initializeTableView];
    [thePageGlyphs setTheClassifier:theClassifier];
    console.log("Finished initializing pageGlyphsTableView");
    // console.log(pageGlyphsSymbolCollectionArrayController);
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
    [self updateClassifierArrayControllerWithResponse:anAction];
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

    console.log("remoteActionDidFinish");
    console.log([anAction result]);
    theClassifier = [[Classifier alloc] initWithJson:[anAction result]];

    console.log("remoteActionDidFinish: theClassifier:");
    console.log(theClassifier);

    [classifierTableViewDelegate setTheGameraGlyphs:theClassifier];

    [symbolTableColumn bind:@"value" toObject:[theClassifier symbolCollectionsArrayController] withKeyPath:@"arrangedObjects.stringAndCountOutput" options:nil];


    [classifierTableViewDelegate initializeTableView];

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

    if ([classifierTableViewDelegate hasSelection])
    {
        [classifierTableViewDelegate writeSymbolName:[aSender stringValue]];
    }
    else
    {
        [pageGlyphsTableViewDelegate writeSymbolName:[aSender stringValue]];
    }
}

- (@action)close:(CPMenuItem)aSender
{
    // TODO: I don't think that we'll need Open and Close in the menu at all

    if (theClassifier)
    {
        if ([theClassifier isDirty])
        {
            [theClassifier ensureSaved];
        }
        theClassifier = null;
    }

    [classifierTableViewDelegate close];
}

- (@action)finishJob:(CPMenuItem)aSender
{
    [self close:null];

    if (thePageGlyphs)
    {
        if ([thePageGlyphs isDirty])
        {
            [thePageGlyphs ensureSaved];
        }
        thePageGlyphs = null;
    }

    [pageGlyphsTableViewDelegate close];
    [pageImageController setContent:null];
    [theRunJob setNeedsInput:false];
    [theRunJob ensureSaved];
    // [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadInteractiveJobsNotification
    //                                       object:nil];  // TODO: Find another way to change the view...
                                                           // this is a data loading notification
}

- (@action)printTheClassifier:(CPButton)aSender  // For debugging
{
    console.log([[[theClassifier symbolCollections][0] glyphList][0] UID]);
    [classifierTableViewDelegate reloadData];
    [pageGlyphsTableViewDelegate reloadData];
}
@end

