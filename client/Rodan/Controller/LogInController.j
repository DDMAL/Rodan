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

    request = [CPURLRequest requestWithURL:@"/auth/"];
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
            alert = [[CPAlert alloc] init];
            [alert setMessageText:@"Incorrect username or password."];
            [alert setAlertStyle:CPWarningAlertStyle];
            [alert addButtonWithTitle:@"Try Again"];
            [alert runModal];

            [connection cancel];
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
