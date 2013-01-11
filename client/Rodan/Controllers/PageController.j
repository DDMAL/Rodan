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

- (id)initWithCoder:(CPCoder)aCoder
{
    if (self = [super init])
    {
        CPLog("Init with Coder called");
    }
}

- (IBAction)uploadFiles:(id)aSender
{
    CPLog("Upload files called");
}

- (void)createObjectsWithJSONResponse:(id)aResponse
{
    CPLog("createObjectsWithJSONResponse pagecontroller");
    [WLRemoteObject setDirtProof:YES];  // turn off auto-creation of pages since we've already done it.
    pages = [Page objectsFromJson:aResponse.pages];
    [pageArrayController addObjects:pages];
    [WLRemoteObject setDirtProof:NO];
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection
{
    CPLog("Did Change Selection");
    var next_page_order = [[pageArrayController contentArray] valueForKeyPath:@"@max.pageOrder"] + 1;
    [imageUploadButton setValue:next_page_order forParameter:@"page_order"];
    [imageUploadButton setValue:activeUser forParameter:@"creator"];
    [button submit];
}

- (void)uploadButton:(UploadButton)button didFailWithError:(CPString)anError
{
    CPLog("Did Fail");
    CPLog(anError);
}

- (void)uploadButton:(UploadButton)button didFinishUploadWithData:(CPString)response
{
    CPLog("Did finish");
    [button resetSelection];
    data = JSON.parse(response)
    [self createObjectsWithJSONResponse:data];
}

- (void)uploadButtonDidBeginUpload:(UploadButton)button
{
    CPLog("Did Begin Upload");
}

- (IBAction)removePage:(id)aSender
{
    var selObjects = [pageArrayController selectedObjects];
    [pageArrayController removeObjects:selObjects];
    [selObjects enumerateObjectsUsingBlock:function(obj, idx, stop)
    {
        [obj delete];
    }];
}

@end
