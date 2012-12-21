@import <AppKit/AppKit.j>
@import <FileUpload/FileUpload.j>
@import <Ratatosk/Ratatosk.j>
@import "../Models/Page.j"


@implementation PageController : CPObject
{
    @outlet     UploadButton        imageUploadButton;
    @outlet     CPImageView         imageView;
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
    console.log(pages);
    [pageArrayController addObjects:pages];
    [WLRemoteObject setDirtProof:NO];
}

- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection
{
    CPLog("Did Change Selection");
    var next_page_order = [[pageArrayController contentArray] valueForKeyPath:@"@max.pageOrder"] + 1;
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

- (IBAction)tableViewSelected:(id)sender
{
    var selectedRow = [sender selectedRow];
    if (selectedRow != -1)
    {
        var selected = [[pageArrayController selection] valueForKey:@"self"];
        console.log(selected);

        [WLRemoteAction schedule:WLRemoteActionGetType path:selected.pk delegate:self message:"Loading projects"];
        console.log(selected.pk)
    }
    else
    {
        //clicked on an empty row - clear the imageView
        [imageView setImage: nil];
    }

    CPLog("Did Select in table");
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    CPLog("Remote Action did Finish");

    var imageData = [CPString stringWithFormat:([anAction result].small_thumb_url)];

    if (imageData != nil)
    {
        var newImage = [[CPImage alloc] initWithContentsOfFile:imageData];
        [imageView setImage: newImage];
    }
}

@end
