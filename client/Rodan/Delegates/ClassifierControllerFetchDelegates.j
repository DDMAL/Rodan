
/*
    The purpose of these delegates is to implement remoteActionDidFinish and
    then call a corresponding classifierController function.  This allows the
    classifierController to do GET requests.
*/

@implementation ClassifierControllerFetchDelegate : CPObject
{
    ClassifierController classifierController;
}

- (id)initWithClassifierController:(ClassifierController)aClassifierController
{
    self = [super init];
    if (self)
    {
        classifierController = aClassifierController;
    }
    return self;
}
@end


@implementation FetchClassifiersDelegate : ClassifierControllerFetchDelegate
{
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController fetchClassifiersDidFinish:anAction];
}
@end

@implementation InitNewFetchClassifiersDelegate : ClassifierControllerFetchDelegate
{
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController initNewFetchClassifiersDidFinish:anAction];
}
@end


@implementation InitImportFetchClassifiersDelegate : ClassifierControllerFetchDelegate
{
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController initImportFetchClassifiersDidFinish:anAction];
}
@end


@implementation InitOpenFetchClassifiersDelegate : ClassifierControllerFetchDelegate
{
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController initOpenFetchClassifiersDidFinish:anAction];
}
@end


@implementation FetchPageGlyphsDelegate : ClassifierControllerFetchDelegate
{
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    [classifierController fetchPageGlyphsDidFinish:anAction];
}
@end
