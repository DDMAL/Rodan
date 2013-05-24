@import <RodanKit/RKInteractiveJob.j>
@import <RodanKit/RKDiva.j>


@import "../Models/RunJob.j"


@global RodanDidLoadInteractiveJobsNotification
@global RodanShouldLoadInteractiveJobsNotification


/**
 * General interactive jobs controller.
 */
@implementation InteractiveJobsController : CPObject
{
    @outlet CPTableView         interactiveJobsTableView;
    @outlet CPArrayController   interactiveJobsArrayController  @accessors(readonly);
            RunJob              currentlySelectedInteractiveJob;
}


- (void)awakeFromCib
{
    // Register self to listen for interactive job array loading (and success).
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(shouldLoadInteractiveJobs:)
                                          name:RodanShouldLoadInteractiveJobsNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(didLoadInteractiveJobs:)
                                          name:RodanDidLoadInteractiveJobsNotification
                                          object:nil];

    // Request loading.
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadInteractiveJobsNotification
                                          object:nil];
}


/**
 * Handle row selection.
 */
- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)aRowIndex
{
    currentlySelectedInteractiveJob = [[interactiveJobsArrayController contentArray] objectAtIndex:aRowIndex];
    return YES;
}


/**
 * Handles the request to load interactive jobs.
 */
- (void)shouldLoadInteractiveJobs:(CPNotification)aNotification
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:"/runjobs/?requires_interaction=1"
                    delegate:self
                    message:"Retrieving RunJobs"];
}


/**
 * Handles success of interactive jobs loading.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        // Go through the RunJobs and take only those that currently require interaction.
        var runJobs = [RunJob objectsFromJson:[aAction result]];
        [interactiveJobsArrayController addObjects:runJobs];
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadInteractiveJobsNotification
                                              object:nil];
    }
}


/**
 * Handles load request notification.  This is here as a dummy, but other classes may need the notification.
 */
- (void)didLoadInteractiveJobs:(CPNotification)aNotification
{
}


/**
 * Loads interactive job window.
 */
- (@action)displayInteractiveJobWindow:(id)aSender
{
    // Get the UUID and give it to a new window.
    var runJobUUID = [currentlySelectedInteractiveJob getUUID];
    var cropWindow = [[RKInteractiveJobWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600)
                                              styleMask:CPClosableWindowMask | CPResizableWindowMask
                                              runJobUUID:runJobUUID];
    [cropWindow center];
    [cropWindow makeKeyAndOrderFront:aSender];
}



/*

- (@action)displayBinariseWindow:(id)aSender
{
    var binariseWindow = [[RKBinariseWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [binariseWindow center];
    [binariseWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayDespeckleWindow:(id)aSender
{
    var despeckleWindow = [[RKDespeckleWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [despeckleWindow center];
    [despeckleWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayRotateWindow:(id)aSender
{
    var rotateWindow = [[RKRotateWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [rotateWindow center];
    [rotateWindow makeKeyAndOrderFront:aSender];
}

- (@action)displaySegmentWindow:(id)aSender
{
    var segmentWindow = [[RKSegmentWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [segmentWindow center];
    [segmentWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayLuminanceWindow:(id)aSender
{
    var luminanceWindow = [[RKLuminanceWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [luminanceWindow center];
    [luminanceWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayBarlineCorrectionWindow:(id)aSender
{
    var barlineCorrectionWindow = [[RKBarlineCorrectionWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask];
    [barlineCorrectionWindow center];
    [barlineCorrectionWindow makeKeyAndOrderFront:aSender];
}

- (@action)displayDivaWindow:(id)aSender
{
    var divaWindow = [[CPWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600) styleMask:CPClosableWindowMask | CPResizableWindowMask],
        divaView = [[RKDiva alloc] initWithFrame:[[divaWindow contentView] bounds]];
    [divaView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable];

    [[divaWindow contentView] addSubview:divaView];
    [divaWindow center];
    [divaWindow makeKeyAndOrderFront:aSender];
}*/
@end
