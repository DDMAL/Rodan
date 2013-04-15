@import <Foundation/CPObject.j>
@import "../Models/Workflow.j"
@import "../Models/Result.j"

@global activeProject
@global RodanDidRefreshWorkflowsNotification
@global RodanDidLoadWorkflowsNotification
@global RodanWorkflowTreeNeedsRefresh


@implementation WorkflowController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
    @outlet     CPArrayController       jobArrayController;
    @outlet     CPArrayController       resultsArrayController;
    @outlet     CPButtonBar             workflowAddRemoveBar;
}

- (void)awakeFromCib
{
    var addButton = [CPButtonBar plusPopupButton],
        removeButton = [CPButtonBar minusButton],
        addWorkflowTitle = @"Add Workflow...";
        // addWorkflowGroupTitle = @"Add Workflow Group";

    [addButton addItemsWithTitles:[addWorkflowTitle]];
    [workflowAddRemoveBar setButtons:[addButton, removeButton]];

    var addWorkflowItem = [addButton itemWithTitle:addWorkflowTitle];

    [addWorkflowItem setAction:@selector(newWorkflow:)];
    [addWorkflowItem setTarget:self];
    [removeButton setAction:@selector(removeWorkflow:)];
    [removeButton setTarget:self];
}

- (void)fetchWorkflows
{
    [WLRemoteAction schedule:WLRemoteActionGetType path:"/workflows" delegate:self message:"Loading workflows"];
}

- (@action)refreshWorkflows:(id)aSender
{
    [self emptyWorkflowArrayController];
    [self fetchWorkflows];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidRefreshWorkflowsNotification
                                          object:nil];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    if ([anAction result])
    {
        var j = [Workflow objectsFromJson:[anAction result]];
        [workflowArrayController addObjects:j];

        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowsNotification
                                              object:[anAction result]];
    }
}

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
    [[workflowArrayController contentArray] removeAllObjects];
}

@end


@implementation WorkflowStatusDelegate : CPObject
{
    @outlet     WorkflowController  workflowController;
    @outlet     RunsStatusDelegate  runsStatusDelegate;
    @outlet     CPArrayController   workflowArrayController;
                CPArrayController   runsArrayController     @accessors(readonly);
    @outlet     CPTableView         runsTableView;
    @outlet     CPTableView         resultsTableView;
}

- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    if ([[[aNotification object] selectedRowIndexes] count] === 0)
    {
        [self emptyArrayControllers];
    }
}

- (void)emptyArrayControllers
{
    [runsArrayController setContent:nil];

    // ensure we empty out the other array controller if we're deslecting the workflow.
    [runsStatusDelegate emptyArrayControllers];
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    runsArrayController = [[CPArrayController alloc] init];
    var workflowObject = [[workflowArrayController contentArray] objectAtIndex:rowIndex];

    [runsArrayController bind:@"contentArray"
                         toObject:workflowObject
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

    return YES;
}

@end

@implementation RunsStatusDelegate : CPObject
{
    @outlet WorkflowStatusDelegate  workflowStatusDelegate;
    @outlet CPTableView             runJobsTableView;
    @outlet CPTableView             pagesTableView;
    @outlet CPTableView             resultsTableView;
            CPArrayController       runJobsArrayController;


    // a bug in cappuccino sends the delegate signal twice. Catch that and only
    // allow the results to be fetched once.
            BOOL                    isFetching;
}

- (void)emptyArrayControllers
{
    [runJobsArrayController setContent:nil];
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
    if (isFetching)
        return;

    isFetching = YES;
    runJobsArrayController = [[CPArrayController alloc] init];
    var run = [[[workflowStatusDelegate runsArrayController] contentArray] objectAtIndex:rowIndex];

    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[run pk] + @"?bypage=true"
                    delegate:self
                    message:"Loading Workflow Run Results"];

    return YES;
}



- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    isFetching = NO;
    [WLRemoteObject setDirtProof:YES];
    var workflowRun = [[WorkflowRun alloc] initWithJson:[anAction result]];
    [WLRemoteObject setDirtProof:NO];


    // [runJobsArrayController bind:@"contentArray"
    //                         toObject:workflowRun
    //                         withKeyPath:@"runJobs"
    //                         options:nil];

    // [runJobsTableView bind:@"content"
    //                   toObject:runJobsArrayController
    //                   withKeyPath:@"arrangedObjects"
    //                   options:nil];

    // [runJobsTableView bind:@"selectionIndexes"
    //                   toObject:runJobsArrayController
    //                   withKeyPath:@"selectionIndexes"
    //                   options:nil];


}

@end


/* we don't need the ratatosk setup for this page representation, so we'll work with a highly simplified model */
@implementation SimplePageModel : CPObject
{
    CPString    pageName    @accessors;
    CPString    pk          @accessors;
}
@end
