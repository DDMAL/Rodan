@import <Foundation/Foundation.j>


@implementation RodanAPIController : CPObject
{
    CPMutableArray  theResult   @accessors;
    CPString        requestURI @accessors;
    CPString        requestMethod @accessors;
    CPString        callbackNotification @accessors;
}

- (id)init
{
    self = [super init];
    if (self)
    {
        theResult = [[CPMutableArray alloc] init];
        requestMethod = @"GET";  // by default
    }
    return self;
}

// + (void)initWithRequest:(CPString)aSection notification:(CPString)aNotification
// {
//     conn = [[self alloc] init];
//     [conn setResultNotification:aNotification];

//     request = [CPURLRequest requestWithURL:"/api/v1/" + aSection + "?format=json"];
//     [request setHTTPMethod:"GET"];
//     var connection = [CPURLConnection connectionWithRequest:request delegate:conn];
// }

- (void)execute
{
    request = [CPURLRequest requestWithURL:requestURI + "?format=json"];
    [request setHTTPMethod:requestMethod];
    conn = [CPURLConnection connectionWithRequest:request delegate:self];
}


- (void)connection:(CPURLConnection)connection didFailWithError:(id)error
{
    CPLog("Failed with Error");
}

- (void)connection:(CPURLConnection)connection didReceiveResponse:(CPURLResponse)response
{
    CPLog("Response Received");
}

- (void)connection:(CPURLConnection)connection didReceiveData:(CPString)data
{
    if (data)
    {
        CPLog(@"Firing notification " + callbackNotification);
        [[CPNotificationCenter defaultCenter] postNotificationName:callbackNotification
                                              object:data
                                              userInfo:nil];
    }
}

@end
