
/*
    This is a very simple class that allows us to observe the state of the
    application and set menu items to be active/inactive as needed.
*/
@implementation MenuItemsController : CPObject
{
    BOOL    statusIsActive      @accessors;
    BOOL    pagesIsActive       @accessors;
    BOOL    jobsIsActive        @accessors;
    BOOL    usersIsActive       @accessors;
    BOOL    resultsIsActive     @accessors;
    BOOL    classifierIsActive  @accessors;
    BOOL    designerIsActive    @accessors;
}

- (void)reset
{
    statusIsActive = NO;
    pagesIsActive = NO;
    jobsIsActive = NO;
    usersIsActive = NO;
    resultsIsActive = NO;
    classifierIsActive = NO;
    designerIsActive = NO;
}

@end
