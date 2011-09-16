var SharedController = nil;

@implementation DjangoAPIController : CPObject
{
    Function addUserCallback;
    Function addUserRequest;
}

+ (DjangoAPIController)sharedController
{
    if (!SharedController)
    {
        SharedController = [[super alloc] init];
    }
    return SharedController;
}

- (void)addUserWithObject:(JSObject)user // callback:aCallback
{
    // Object is a dictionary with values accessed as follows: user.email, user.username, user.realName, user.institution;
    console.log("DJANGO API CONTROLLER ADDS THIS USER: " + user);

    // VERY HIGH CHANCE OF RUNNING INTO PROBLEMS WITH ASYNCHRONICITY AND CALLBACKS
    // But using CFHTTPRequest() seems too difficult so it'll have to be done this way for now
    request = [[CPURLRequest alloc] initWithURL:@"http://localhost:8000/api/v1/user/"];
    [request setHTTPMethod:@"POST"];
    var data = [CPString JSONFromObject:user];
    console.log(data);
    [request setHTTPBody:data];
    [request setValue:"application/json; charset=UTF-9" forHTTPHeaderField:@"Content-Type"];
    var connection = [CPURLConnection connectionWithRequest:request delegate:self];
    var addUserCallback = function() {
        console.log("here's the callback");
    };
    var addUserRequest = request;
}

- (void)connection:aConnection didReceiveData:data
{
    console.log(data);
    addUserCallback(addUserRequest);
}

@end