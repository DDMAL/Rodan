@import <Foundation/CPObject.j>
@import <RodanKit/Utilities/RKNotificationTimer.j>
@import "../Models/Workflow.j"
@import "../Models/Result.j"

@global activeProject
@global activeUser
@global RodanDidRefreshWorkflowsNotification
@global RodanDidLoadWorkflowsNotification
@global RodanWorkflowTreeNeedsRefresh
@global RodanHasFocusWorkflowResultsViewNotification
@global RodanShouldLoadWorkflowResultsNotification


var activeWorkflow = nil,
    _msLOADINTERVAL = 5.0;


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CONTROLLERS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * General workflow controller that exists with the Workflow Results View.
 * It's purpose is to do a lot of reload handling.
 */
@implementation WorkflowController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
    @outlet     CPArrayController       jobArrayController;
    @outlet     CPArrayController       resultsArrayController;
    @outlet     CPButtonBar             workflowAddRemoveBar;
    @outlet     WorkflowStatusDelegate  workflowStatusDelegate;
    @outlet     RunsStatusDelegate      workflowRunsStatusDelegate;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Init Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)awakeFromCib
{
    var addButton = [CPButtonBar plusPopupButton],
        removeButton = [CPButtonBar minusButton],
        addWorkflowTitle = @"Add Workflow...";

    [addButton addItemsWithTitles:[addWorkflowTitle]];
    [workflowAddRemoveBar setButtons:[addButton, removeButton]];

    var addWorkflowItem = [addButton itemWithTitle:addWorkflowTitle];

    [addWorkflowItem setAction:@selector(newWorkflow:)];
    [addWorkflowItem setTarget:self];
    [removeButton setAction:@selector(removeWorkflow:)];
    [removeButton setTarget:self];

    [removeButton bind:@"enabled"
                  toObject:workflowArrayController
                  withKeyPath:@"selectedObjects.@count"
                  options:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(receiveHasFocusEvent:)
                                          name:RodanHasFocusWorkflowResultsViewNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(shouldLoad:)
                                          name:RodanShouldLoadWorkflowResultsNotification
                                          object:nil];
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)removeWorkflow:(id)aSender
{
    if ([workflowArrayController selectedObjects])
    {
        var alert = [CPAlert alertWithMessageText:@"You are about to permanently delete this workflow"
                             defaultButton:@"Delete"
                             alternateButton:@"Cancel"
                             otherButton:nil
                             informativeTextWithFormat:nil];
        [alert setDelegate:self];
        [alert runModal];
    }
}


- (void)newWorkflow:(id)aSender
{
    var wflow = [[Workflow alloc] init];
    [wflow setProjectURL:[activeProject pk]];
    [wflow setWorkflowCreator:[activeUser pk]];
    [workflowArrayController addObject:wflow];
    [wflow ensureCreated];
}


- (void)alertDidEnd:(CPAlert)theAlert returnCode:(int)returnCode
{
    if (returnCode == 0)
    {
        var selectedObjects = [workflowArrayController selectedObjects];
        [workflowArrayController removeObjects:selectedObjects];
        [selectedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
    }
}


- (void)emptyWorkflowArrayController
{
    [workflowArrayController setContent:nil];
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)receiveHasFocusEvent:(CPNotification)aNotification
{
    [RKNotificationTimer setTimedNotification:_msLOADINTERVAL
                         notification:RodanShouldLoadWorkflowResultsNotification];
}


/**
 * Handles the request to load.
 */
- (void)shouldLoad:(CPNotification)aNotification
{
    // Reload the runs of the currently selected workflow.
    if ([workflowStatusDelegate currentlySelectedWorkflow] != nil)
    {
        // Remote call.
        [WLRemoteAction schedule:WLRemoteActionGetType
                        path:[[workflowStatusDelegate currentlySelectedWorkflow] remotePath]
                        delegate:self
                        message:"Loading Workflow"];
    }
}


/**
 * Handles success of loading.
 */
- (void)remoteActionDidFinish:(WLRemoteAction)aAction
{
    if ([aAction result])
    {
        [WLRemoteObject setDirtProof:YES];
        [[workflowStatusDelegate currentlySelectedWorkflow] initWithJson:[aAction result]];
        [WLRemoteObject setDirtProof:NO];
        [workflowStatusDelegate bindWorkflowRuns];
    }
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Static Methods
////////////////////////////////////////////////////////////////////////////////////////////
+ (Workflow)activeWorkflow
{
    return activeWorkflow;
}


+ (void)setActiveWorkflow:(Workflow)aWorkflow
{
    activeWorkflow = aWorkflow;
    console.log("active workflow: " + [activeWorkflow workflowName]);
}
@end


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DELEGATES
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Delegate for the Workflow table view in the Workflow Status view.
 */
@implementation WorkflowStatusDelegate : CPObject
{
    @outlet     WorkflowController  workflowController;
    @outlet     RunsStatusDelegate  runsStatusDelegate;
    @outlet     CPArrayController   workflowArrayController;
                CPArrayController   runsArrayController         @accessors(readonly);
    @outlet     CPTableView         runsTableView;
    @outlet     CPTableView         resultsTableView;
                Workflow            currentlySelectedWorkflow   @accessors(readonly);
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)emptyArrayControllers
{
    [runsArrayController setContent:nil];
    [runsStatusDelegate emptyArrayControllers];
}


/**
 * Binds array controller for Workflow Runs to the table view.
 */
- (void)bindWorkflowRuns
{
    [runsArrayController bind:@"contentArray"
                         toObject:currentlySelectedWorkflow
                         withKeyPath:@"workflowRuns"
                         options:nil];

    [runsTableView bind:@"content"
                   toObject:runsArrayController
                   withKeyPath:@"arrangedObjects"
                   options:nil];

    [runsTableView bind:@"selectionIndexes"
                   toObject:runsArrayController
                   withKeyPath:@"selectionIndexes"
                   options:nil];
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    if ([[[aNotification object] selectedRowIndexes] count] === 0)
    {
        [self emptyArrayControllers];
    }
}


- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    [self emptyArrayControllers];
    runsArrayController = [[CPArrayController alloc] init];
    currentlySelectedWorkflow = [[workflowArrayController contentArray] objectAtIndex:rowIndex];
    [WorkflowController setActiveWorkflow:currentlySelectedWorkflow];
    [self bindWorkflowRuns];
    return YES;
}


@end



///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// RunsStatusDelegate
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@implementation RunsStatusDelegate : CPObject
{
    @outlet WorkflowStatusDelegate  workflowStatusDelegate;
    @outlet CPTableView             runJobsTableView;
    @outlet CPTableView             pagesTableView;
    @outlet CPTableView             resultsTableView;
            CPArrayController       runJobsArrayController;
            CPArrayController       pagesArrayController;
            CPArrayController       resultsArrayController;
}

- (void)emptyArrayControllers
{
    [runJobsArrayController setContent:nil];
    [pagesArrayController setContent:nil];
    [resultsArrayController setContent:nil];
}


- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    if ([[[aNotification object] selectedRowIndexes] count] === 0)
    {
        [self emptyArrayControllers];
    }

}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    runJobsArrayController = [[CPArrayController alloc] init];
    var run = [[[workflowStatusDelegate runsArrayController] contentArray] objectAtIndex:rowIndex];

    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[run pk] + @"?by_page=true"  // return results by page, rather than by run_job
                    delegate:self
                    message:"Loading Workflow Run Results"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    var workflowRun = [[SimpleWorkflowRunModel alloc] initWithJson:[anAction result]];

    pagesArrayController = [[CPArrayController alloc] init];
    resultsArrayController = [[CPArrayController alloc] init];

    [pagesArrayController bind:@"contentArray"
                          toObject:workflowRun
                          withKeyPath:@"pages"
                          options:nil];

    [pagesTableView bind:@"content"
                    toObject:pagesArrayController
                    withKeyPath:@"arrangedObjects"
                    options:nil];

    [pagesTableView bind:@"selectionIndexes"
                    toObject:pagesArrayController
                    withKeyPath:@"selectionIndexes"
                    options:nil];

    [resultsArrayController bind:@"contentArray"
                            toObject:pagesArrayController
                            withKeyPath:@"selection.results"
                            options:nil];

    [resultsTableView bind:@"content"
                      toObject:resultsArrayController
                      withKeyPath:@"arrangedObjects"
                      options:nil];

    [resultsTableView bind:@"selectionIndexes"
                      toObject:resultsArrayController
                      withKeyPath:@"selectionIndexes"
                      options:nil];
}

@end



/* we don't need the ratatosk setup for these model representations, so we'll work with a highly simplified model */

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SimplePageModel
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@implementation SimplePageModel : CPObject
{
    CPString    pageName    @accessors;
    CPNumber    pageOrder   @accessors;
    CPString    pk          @accessors;
    CPArray     results     @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    var mapping = [
        ['pk', 'url'],
        ['pageName', 'name'],
        ['pageOrder', 'page_order'],
        ['results', 'results'],
        ];

    var i = 0,
        count = mapping.length;

    for (; i < count; i++)
    {
        var map = mapping[i],
            resultArray = [];
        if (map[1] == "results")
        {
            var j = 0,
                resCount = jsonObject['results'].length;

            for (; j < resCount; j++)
            {
                var res = [[SimpleResultsModel alloc] initWithJson:jsonObject['results'][j]];
                [resultArray addObject:res];
            }
            [self setValue:resultArray forKey:map[0]];
        }
        else
        {
            [self setValue:jsonObject[map[1]] forKey:map[0]];
        }
    }

    return self;
}
@end



///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SimpleWorkflowRunModel
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@implementation SimpleWorkflowRunModel : CPObject
{
    CPString    pk          @accessors;
    CPString    workflow    @accessors;
    CPNumber    run         @accessors;
    BOOL        testRun     @accessors;
    CPArray     pages       @accessors;
    CPString    created     @accessors;
    CPString    updated     @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    var mapping = [
        ['pk', 'url'],
        ['workflow', 'workflow'],
        ['run', 'run'],
        ['testRun', 'test_run'],
        ['pages', 'pages'],
        ['created', 'created'],
        ['updated', 'updated']
        ];

    var i = 0,
        count = mapping.length;

    for (; i < count; i++)
    {
        var map = mapping[i],
            pageArray = [];

        if (map[1] === "pages")
        {
            var j = 0,
                pageCount = jsonObject['pages'].length;

            for (; j < pageCount; j++)
            {
                var page = [[SimplePageModel alloc] initWithJson:jsonObject['pages'][j]];
                [pageArray addObject:page];
            }
            [self setValue:pageArray forKey:map[0]];
        }
        else
        {
            [self setValue:jsonObject[map[1]] forKey:map[0]];
        }
    };

    return self;
}
@end



///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SimpleResultsModel
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@implementation SimpleResultsModel : CPObject
{
    CPString    created         @accessors;
    CPString    mediumThumbURL  @accessors;
    CPString    result          @accessors;
    CPString    runJob          @accessors;
    CPString    runJobName      @accessors;
    CPString    pk              @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    var mapping = [
        ['created', 'created'],
        ['mediumThumbURL', 'medium_thumb_url'],
        ['result', 'result'],
        ['runJob', 'run_job'],
        ['runJobName', 'run_job_name'],
        ['pk', 'url']
        ];

    var i = 0,
        count = mapping.length;
    for (; i < count; i++)
    {
        var map = mapping[i];
        [self setValue:jsonObject[map[1]] forKey:map[0]];
    }

    return self;
}

@end
