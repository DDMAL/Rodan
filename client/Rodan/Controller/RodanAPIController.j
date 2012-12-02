@import <Foundation/Foundation.j>


@implementation RodanAPIController : CPObject
{
    CPMutableArray  theResult   @accessors;
    CPString        resultNotification @accessors;
}

- (id)init
{
    self = [super init];
    if (self)
    {
        theResult = [[CPMutableArray alloc] init];
    }
    return self;
}

+ (id)initWithRequest:(CPString)aSection notification:(CPString)aNotification
{
    var r = [[self alloc] init],
        request = [CPURLRequest requestWithURL:"/api/v1/" + aSection + "?format=json"];

    [r setResultNotification:aNotification];

    [request setHTTPMethod:"GET"];
    var connection = [CPURLConnection connectionWithRequest:request delegate:r];

    return r;
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
        var j = JSON.parse(data);

        for (var i = j.objects.length - 1; i >= 0; i--)
        {
            var p = [Project projectWithObject:j.objects[i]];
            [theResult addObject:p];
        };

        CPLog(@"Firing notification " + resultNotification);
        // [[CPNotificationCenter defaultCenter] postNotificationName:resultNotification
                                              object:theResult
                                              userInfo:nil];
    }
}

@end
