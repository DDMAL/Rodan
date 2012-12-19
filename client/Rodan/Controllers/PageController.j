@import <FileUpload/FileUpload.j>
@import "../Models/Page.j"


@implementation PageController : CPObject
{
    @outlet     UploadButton        imageUploadButton;
    @outlet     CPArrayController   pageArrayController;
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
    [WLRemoteObject setDirtProof:YES];  // turn off auto-creation of pages since we've already done it.
    pages = [Page objectsFromJson:aResponse.pages];
    [pageArrayController addObjects:pages];
    [WLRemoteObject setDirtProof:NO];
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection
{
    CPLog("Did Change Selection");
    max = [[pageArrayController contentArray] valueForKeyPath:@"@max.pageOrder"];
    next_page_order = max + 1;
    [imageUploadButton setValue:next_page_order forParameter:@"page_order"];
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

@end
