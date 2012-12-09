@import <AppKit/AppKit.j>

@implementation LogInController : CPObject
{
    @outlet     CPTextField       usernameField;
    @outlet     CPSecureTextField passwordField;
}

- (IBAction)logIn:(id)aSender
{
    CPLog("Calling Log In");
    username = [usernameField objectValue];
    password = [passwordField objectValue];

    request = [CPURLRequest requestWithURL:@"/auth/session/"];
    [request setValue:@"application/json" forHTTPHeaderField:@"Accept"];
    [request setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"]
    [request setHTTPBody:@"username=" + username + "&password=" + password];
    [request setHTTPMethod:@"POST"];

    conn = [CPURLConnection connectionWithRequest:request delegate:self];
}

- (void)connection:(CPURLConnection)connection didFailWithError:(id)error
{
    CPLog("Failed with Error");
}

- (void)connection:(CPURLConnection)connection didReceiveResponse:(CPURLResponse)response
{
    CPLog("Response Received");

    switch ([response statusCode])
    {
        case 400:
            CPLog("Received 400 Bad Request");
            alert = [[CPAlert alloc] init];
            [alert setMessageText:@"Error."];
            [alert setAlertStyle:CPWarningAlertStyle];
            [alert addButtonWithTitle:@"Try Again"];
            [alert runModal];

            [connection cancel];
        case 401:
            // UNAUTHORIZED
            CPLog("Received 401 Unauthorized");
            [[CPNotificationCenter defaultCenter] postNotificationName:RodanMustLogInNotification
                                      object:nil
                                      userInfo:nil];

            [connection cancel];
            break;
        case 403:
            // FORBIDDEN
            CPLog("Received 403 Forbidden");
            [[CPNotificationCenter defaultCenter] postNotificationName:RodanCannotLogInNotification
                                      object:nil
                                      userInfo:nil];

            [connection cancel]
            break;
        case 404:
            // NOT FOUND
            CPLog("Received 404 Not Found");
            break;
        default:
            console.log("I received a status code of " + [response statusCode]);
    }
}

- (void)connection:(CPURLConnection)connection didReceiveData:(CPString)data
{
    if (data)
    {
        CPLog(@"Firing notification " + RodanDidLogInNotification);
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLogInNotification
                                              object:data
                                              userInfo:nil];
    }
}

@end


@implementation LogInCheckController : CPObject
{
    CPURLConnection conn;
}

- (LogInCheckController)initCheckingStatus
{
    if (self = [super init])
    {
        request = [CPURLRequest requestWithURL:@"/auth/status/"];
        [request setHTTPMethod:@"GET"];
        conn = [CPURLConnection connectionWithRequest:request delegate:self];
    }
    return self;
}

- (void)connection:(CPURLConnection)connection didFailWithError:(id)error
{
    CPLog("Failed with Error");
}

- (void)connection:(CPURLConnection)connection didReceiveResponse:(CPURLResponse)response
{
    CPLog("Response Received");

    switch ([response statusCode])
    {
        case 200:
            // Success
            CPLog("Received 200 Success");
            break;
        case 400:
            // BAD REQUEST
            CPLog("Received 400 Bad Request");
            [connection cancel];
        case 401:
            // UNAUTHORIZED
            CPLog("Received 401 Unauthorized");
            [[CPNotificationCenter defaultCenter] postNotificationName:RodanMustLogInNotification
                                                  object:nil];
            [connection cancel];
            break;
        case 403:
            // FORBIDDEN
            CPLog("Received 403 Forbidden");
            [[CPNotificationCenter defaultCenter] postNotificationName:RodanCannotLogInNotification
                                                  object:nil];
            [connection cancel];
            break;
        case 404:
            // NOT FOUND
            CPLog("Received 404 Not Found");
            [connection cancel];
            break;
        default:
            console.log("I received a status code of " + [response statusCode]);
    }
}

- (void)connection:(CPURLConnection)connection didReceiveData:(CPString)data
{
    if (data)
    {
        var data = JSON.parse(data),
            resp = [CPDictionary dictionaryWithJSObject:data];
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLogInNotification
                                              object:resp ];
    }
}

@end
