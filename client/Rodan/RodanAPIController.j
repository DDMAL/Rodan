@import <Foundation/Foundation.j>


var RODAN = "http://localhost:8000/api/v1";

@implementation RodanAPIController : CPObject
{
    CPMutableArray  theResult   @accessors;
    CPString        resultNotification @accessors;
}

- (id)init
{
    self = [super init];
    return self;
}

+ (id)initWithRequest:(CPString)aSection notification:(CPString)aNotification
{
    console.log("Firing REquest");
    var r = [[self alloc] init],
        request = [CPURLRequest requestWithURL:"http://localhost:8000/api/v1/" + aSection + "?format=json"];

    [r setResultNotification:aNotification];
    [r setTheResult:[CPMutableArray init]];

    [request setHTTPMethod:"GET"];
    var connection = [CPURLConnection connectionWithRequest:request delegate:r];

    return r;
}

- (void)connection:(CPURLConnection)connection didFailWithError:(id)error
{
    console.log("Oops, Error");
}

- (void)connection:(CPURLConnection)connection didReceiveResponse:(CPURLResponse)response
{
    console.log("Reeespooonse!");
    console.log([response statusCode]);
}

- (void)connection:(CPURLConnection)connection didReceiveData:(CPString)data
{
    console.log([theResult]);
    var j = JSON.parse(data);
    for (var i = j.objects.length - 1; i >= 0; i--)
    {
        [theResult addObject:[Project projectWithObject:j.objects[i]]];
    };

    console.log([theResult]);

    [[CPNotificationCenter defaultCenter] postNotificationName:resultNotification
                                          object:nil
                                          userInfo:nil];
}

@end
