@import <FileUpload/FileUpload.j>


@implementation PageController : CPObject
{
    @outlet     UploadButton    imageUploadButton;
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


- (void)uploadButton:(UploadButton)button didChangeSelection:(CPArray)selection
{
    CPLog("Did Change Selection");
    console.log(selection);
    [button submit];
}

- (void)uploadButton:(UploadButton)button didFailWithError:(CPString)anError
{
    CPLog("Did Fail");
}

- (void)uploadButton:(UploadButton)button didFinishUploadWithData:(CPString)response
{
    CPLog("Did Finish");
    [button resetSelection];
}

- (void)uploadButtonDidBeginUpload:(UploadButton)button
{
    CPLog("Did Begin Upload");
}

@end
