@import <AppKit/AppKit.j>
@import <FileUpload/FileUpload.j>
@import <Ratatosk/Ratatosk.j>
@import "../Models/Page.j"


@implementation PageController : CPObject
{
    @outlet     UploadButton        imageUploadButton;
    @outlet     CPImageView         imageView;
    @outlet     CPArrayController   pageArrayController;
    @outlet     CPTextField         sizeField;
    @outlet     CPTextField         dateAddedField;
    @outlet     CPTextField         addedByField;
}

- (void)awakeFromCib
{
    var formatter = [[CPDateFormatter alloc] init];
    [formatter setDateStyle:CPDateFormatterMediumStyle];
    [dateAddedField setFormatter:formatter];
}

- (id)initWithCoder:(CPCoder)aCoder
{
    var self = [super initWithCoder:aCoder];
    if (self)
    {
    }

    return self;
}

- (IBAction)uploadFiles:(id)aSender
{
}

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
    [pageArrayController removeObjects:selectedObjects];
    [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
}

- (void)emptyPageArrayController
{
    [[pageArrayController contentArray] removeAllObjects];
}

@end
