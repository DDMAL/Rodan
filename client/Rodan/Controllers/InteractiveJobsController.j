@import <Foundation/CPTimer.j>
@import <RodanKit/RKInteractiveJob.j>
@import <RodanKit/RKDiva.j>
@import <RodanKit/Utilities/RKNotificationTimer.j>


@import "../Models/RunJob.j"


@global RodanHasFocusInteractiveJobsViewNotification
@global RodanShouldLoadInteractiveJobsNotification
@global activeProject


var _msLOADINTERVAL = 5.0;


/**
 * General interactive jobs controller.
 */
@implementation InteractiveJobsController : CPObject
{
    @outlet CPTableView         interactiveJobsTableView;
    @outlet CPArrayController   interactiveJobsArrayController  @accessors(readonly);
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
    var projectUUID = nil;
    if (activeProject != nil)
    {
        projectUUID = [activeProject uuid];
    }
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:"/runjobs/?requires_interaction=true&project=" + projectUUID
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
        var runJobs = [RunJob objectsFromJson:[aAction result]];
        [interactiveJobsArrayController setContent:runJobs];
    }
}


/**
 * Loads interactive job window.
 */
- (@action)displayInteractiveJobWindow:(id)aSender
{
    // Get the UUID and give it to a new window.
    var runJob = [[interactiveJobsArrayController selectedObjects] objectAtIndex:0],
        runJobUUID = [runJob getUUID],
        jobName = [runJob jobName],
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
