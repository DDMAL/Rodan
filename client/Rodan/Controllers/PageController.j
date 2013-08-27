@import <AppKit/AppKit.j>
@import <FileUpload/FileUpload.j>
@import <Ratatosk/Ratatosk.j>
@import "../Models/Page.j"

@global activeProject
@global RodanHasFocusPagesViewNotification
@global RodanShouldLoadPagesNotification

var _msLOADINTERVAL = 5.0;

@implementation PageController : CPObject
{
    @outlet     UploadButton        imageUploadButton;
    @outlet     CPImageView         imageView;
    @outlet     CPArrayController   pageArrayController;
    @outlet     CPTextField         sizeField;
    @outlet     CPTextField         dateAddedField;
    @outlet     CPTextField         addedByField;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Init Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)awakeFromCib
{
    // var formatter = [[CPDateFormatter alloc] init];
    // [formatter setDateStyle:CPDateFormatterMediumStyle];
    // [dateAddedField setFormatter:formatter];
    var byteCountFormatter = [[CPByteCountFormatter alloc] init];
    [sizeField setFormatter:byteCountFormatter];

    // Subscriptions for self.
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(receiveHasFocusEvent:)
                                          name:RodanHasFocusPagesViewNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(handleShouldLoadNotification:)
                                          name:RodanShouldLoadPagesNotification
                                          object:nil];
}

- (id)initWithCoder:(CPCoder)aCoder
{
    var self = [super initWithCoder:aCoder];
    if (self)
    {
    }

    return self;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)createObjectsWithJSONResponse:(id)aResponse
{
    [WLRemoteObject setDirtProof:YES];  // turn off auto-creation of pages since we've already done it.
    var pages = [Page objectsFromJson:aResponse.pages];
    [pageArrayController addObjects:pages];
    [WLRemoteObject setDirtProof:NO];
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection
{
    var nextPageOrder = [[pageArrayController contentArray] valueForKeyPath:@"@max.pageOrder"] + 1;
    [imageUploadButton setValue:[activeProject pk] forParameter:@"project"];
    [imageUploadButton setValue:nextPageOrder forParameter:@"page_order"];

    [button submit];
}

- (void)uploadButton:(UploadButton)button didFailWithError:(CPString)anError
{
    CPLog.error(anError);
}

- (void)uploadButton:(UploadButton)button didFinishUploadWithData:(CPString)response
{
    [button resetSelection];
    var data = JSON.parse(response);
    [self createObjectsWithJSONResponse:data];
}

- (void)uploadButtonDidBeginUpload:(UploadButton)button
{
    CPLog("Did Begin Upload");
}

- (IBAction)removePage:(id)aSender
{
    var selectedObjects = [pageArrayController selectedObjects];
    [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
    [self handleShouldLoadNotification:null];
}

- (void)emptyPageArrayController
{
    [pageArrayController setContent:nil];
}

/**
 * Does a page load request.
 */
- (void)sendLoadRequest
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:@"pages?project=" + [activeProject uuid]
                    delegate:self
                    message:"Loading Workflow Run Results"];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)receiveHasFocusEvent:(CPNotification)aNotification
{
    [RKNotificationTimer setTimedNotification:_msLOADINTERVAL
                         notification:RodanShouldLoadPagesNotification];
}

/**
 * Handles load notification
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    [self sendLoadRequest];
}

/**
 * Handles remote object load.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];
        var pageArray = [Page objectsFromJson:[aAction result]];
        [pageArrayController setContent:pageArray];
        [WLRemoteObject setDirtProof:NO];
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
// Action Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Initializes packaging of results.
 */
- (@action)viewOriginal:(id)aSender
{
    var selectedObjects = [pageArrayController selectedObjects];
    if ([selectedObjects count] == 1)
    {
        window.open([[selectedObjects objectAtIndex:0] pageImage], "_blank");
    }
}
@end
