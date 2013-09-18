/*
    UploadWindowController exists because we have a couple of cappuccino windows
    that allow you to upload a file that are the same.

    It's pretty much a mini controller.  It even does a GET to the list URL and updates
    the array controller.  It does so generically - it gets the model class out of the
    array controller [arrayController objectClass], which is linked through the cib.
    (The class of the model we're using is set in the array controller properties in
    XCode.)

    It's actually pretty cool.  You initialize this thing in XCode and set up all the outlets,
    and it does everything, generically.  It's working now for classifiers and for
    classifierSettings.  It does everything that the upload window needs anyway.  The modelListUrl
    must be initialized in XCode also.  It's nice to do everything in XCode because you don't have
    to worry about dependencies or initialize this thing in code: it's properly scoped (global)
    when it's an XCode object.

    The window uses an "UploadButton" to do the POST.  The way it works is that fields are set on the
    UploadButton, and then you call 'submit' to execute the POST request.
    The UploadButton is actually the one marked "Choose..." (chooseFileButton,) and
    the button marked "Submit" simply sends the 'submit' message to the other button.  The reason for
    this is usability: I wanted the user to choose a file and then submit it in two actions, to give
    them a chance to look at the name and the file together before confirming.
*/

@global activeProject

@implementation UploadWindowController : CPObject
{
    @outlet CPWindow cappuccinoWindow;
    @outlet UploadButton chooseFileButton;
    @outlet CPButton submitButton;
    @outlet CPTextField nameTextField;
    @outlet CPTextField fileTextField;
    @outlet CPTextField nameUsedLabel;
    @outlet CPArrayController arrayController @accessors;

    CPString modelListUrl @accessors;  // initialized in XCode (Identity tab)
}

- (id)awakeFromCib
{
    [cappuccinoWindow setDefaultButton:submitButton];

    // Initialize the upload button
    // The button also has a CSRF token that is initialized in ClassifierViewController
    [chooseFileButton setBordered:YES];
    [chooseFileButton setFileKey:@"files"];
    [chooseFileButton allowsMultipleFiles:NO];
    [chooseFileButton setDelegate:self];
    [chooseFileButton setURL:modelListUrl];
}

- (void)openWindow
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[self modelListUrl]
                    delegate:self
                    message:"Loading classifier settings list"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    var models = [[arrayController objectClass] objectsFromJson:[anAction result]];
    [arrayController setContent:models];
    [nameTextField setStringValue:@""];
    [fileTextField setStringValue:@""];
    [nameUsedLabel setHidden:YES];
    [chooseFileButton resetSelection];
    [cappuccinoWindow makeKeyAndOrderFront:null];
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection  // Delegate method for uploading XML
{
    var oldNameFromFile = [self clipFileExtension:[fileTextField stringValue]],
        currentName = [nameTextField stringValue];

    if (currentName === @"" || currentName === oldNameFromFile)
    {
        // Update the Name textfield if it's empty or the user hasn't changed anything
        var newName = [self clipFileExtension:selection];

        [nameTextField setStringValue:newName];
        [self updateNameUsedLabel];
    }

    [fileTextField setStringValue:selection];
}


- (@action)uploadModel:(CPButton)submitButton
{
    var newName = [nameTextField stringValue];

    if (newName === @"")
    {
        [nameUsedLabel setStringValue:@"Name cannot be blank."];
        [nameUsedLabel setHidden:NO];
    }
    else if ([fileTextField stringValue] === @"")
    {
        [nameUsedLabel setStringValue:@"Choose a file to upload."];
        [nameUsedLabel setHidden:NO];
    }
    else if ([self modelExists:newName])
    {
        [self updateNameUsedLabel];
    }
    else
    {
        [chooseFileButton setValue:[activeProject pk] forParameter:@"project"];
        [chooseFileButton setValue:[nameTextField stringValue] forParameter:@"name"];
        [chooseFileButton submit];  // Sends a POST to modelListUrl (ie: /classifiers/) (see awakeFromCib)
    }
}

- (void)uploadButtonDidBeginUpload:(UploadButton)button  // Delegate method for uploading XML
{
    // This function is called when upload button is pressed.
    // It's not needed because uploadModel: does the job.
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
    [cappuccinoWindow close];
}

- (void)createObjectsWithJSONResponse:(id)aResponse
{
    [WLRemoteObject setDirtProof:YES];
    var newModel = [[[self arrayController] objectClass] objectsFromJson:[aResponse]];
    [arrayController addObjects:newModel];
    [WLRemoteObject setDirtProof:NO];
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

- (void)updateNameUsedLabel
{
    if ([self modelExists:[nameTextField stringValue]])
    {
        [nameUsedLabel setStringValue:@"Name unavailable."];
        [nameUsedLabel setHidden:NO];
    }
    else
    {
        [nameUsedLabel setHidden:YES];
    }
}

- (Boolean)modelExists:(CPString)modelName
{
    var i = 0,
        array = [arrayController contentArray],
        count = [array count];

    for (; i < count; ++i)
    {
        if (modelName === [array[i] name])
        {
            return true;
        }
    }

    return false;
}

// Textfield delegate method
- (void)controlTextDidChange:(CPNotification)aNotification
{
    [self updateNameUsedLabel];
}

@end
