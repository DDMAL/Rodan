@import <Foundation/CPTimer.j>
@import <RodanKit/RKInteractiveJob.j>
@import <RodanKit/RKDiva.j>
@import <RodanKit/Utilities/RKNotificationTimer.j>


@import "../Models/RunJob.j"


@global RodanHasFocusInteractiveJobsViewNotification
@global RodanShouldLoadInteractiveJobsNotification


var _msLOADINTERVAL = 5.0;


/**
 * General interactive jobs controller.
 */
@implementation InteractiveJobsController : CPObject
{
    @outlet CPTableView         interactiveJobsTableView;
    @outlet CPArrayController   interactiveJobsArrayController  @accessors(readonly);
            RunJob              currentlySelectedInteractiveJob;
            CPTimer             timer;
}


- (void)awakeFromCib
{
    // Register self to listen for interactive job array loading (and success).
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(shouldLoad:)
                                          name:RodanShouldLoadInteractiveJobsNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(receiveHasFocusEvent:)
                                          name:RodanHasFocusInteractiveJobsViewNotification
                                          object:nil];
}


- (void)receiveHasFocusEvent:(CPNotification)aNotification
{
    [RKNotificationTimer setTimedNotification:_msLOADINTERVAL
                         notification:RodanShouldLoadInteractiveJobsNotification];
}


/**
 * Handles the request to load interactive jobs.
 */
- (void)shouldLoad:(CPNotification)aNotification
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:"/runjobs/?requires_interaction=true"
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
        // Populate the array controller, set the new "currently active", and send notification.
        var runJobs = [RunJob objectsFromJson:[aAction result]];
        [interactiveJobsArrayController setContent:runJobs];
        if ([[interactiveJobsArrayController contentArray] count] > 0)
        {
            currentlySelectedInteractiveJob = [[interactiveJobsArrayController contentArray] objectAtIndex:0];
        }
    }
}


/**
 * Loads interactive job window.
 */
- (@action)displayInteractiveJobWindow:(id)aSender
{
    // Get the UUID and give it to a new window.
    var runJobUUID = [currentlySelectedInteractiveJob getUUID],
        jobName = [currentlySelectedInteractiveJob jobName],
        cropWindow = [[RKInteractiveJobWindow alloc] initWithContentRect:CGRectMake(0, 0, 800, 600)
                                              styleMask:CPClosableWindowMask | CPResizableWindowMask
                                              runJobUUID:runJobUUID
                                              jobName:jobName];
    [cropWindow center];
    [cropWindow makeKeyAndOrderFront:aSender];
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DELEGATE METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Handle row selection.
 */
- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)aRowIndex
{
    currentlySelectedInteractiveJob = [[interactiveJobsArrayController contentArray] objectAtIndex:aRowIndex];
    return YES;
}

/*


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
