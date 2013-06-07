@import <Foundation/CPObject.j>
@import <RodanKit/Utilities/RKNotificationTimer.j>
@import "../Delegates/ResultsViewRunsDelegate.j"
@import "../Delegates/ResultsViewWorkflowsDelegate.j"
@import "../Models/Workflow.j"


@global activeProject
@global activeUser
@global RodanDidRefreshWorkflowsNotification
@global RodanDidLoadWorkflowsNotification
@global RodanWorkflowTreeNeedsRefresh
@global RodanHasFocusWorkflowResultsViewNotification
@global RodanShouldLoadWorkflowResultsWorkflowsNotification
@global RodanShouldLoadWorkflowResultsWorkflowRunsNotification
@global RodanShouldLoadWorkflowResultsWorkflowResultsNotification


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
    @outlet     CPArrayController               workflowArrayController;
    @outlet     CPArrayController               workflowPagesArrayController;
    @outlet     CPButtonBar                     workflowAddRemoveBar;
    @outlet     ResultsViewWorkflowsDelegate    resultsViewWorkflowsDelegate;
    @outlet     ResultsViewRunsDelegate         resultsViewRunsDelegate;
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

    // Subscriptions for self.
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(receiveHasFocusEvent:)
                                          name:RodanHasFocusWorkflowResultsViewNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(handleShouldLoadNotification:)
                                          name:RodanShouldLoadWorkflowResultsWorkflowsNotification
                                          object:nil];

    // Subscriptions for delegates.
    [[CPNotificationCenter defaultCenter] addObserver:resultsViewWorkflowsDelegate
                                          selector:@selector(handleShouldLoadNotification:)
                                          name:RodanShouldLoadWorkflowResultsWorkflowRunsNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] addObserver:resultsViewRunsDelegate
                                          selector:@selector(handleShouldLoadNotification:)
                                          name:RodanShouldLoadWorkflowResultsWorkflowResultsNotification
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
// Action Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Runs the currently selected workflow.
 */
- (@action)runWorkflow:(id)aSender
{
    var workflow = [[workflowArrayController selectedObjects] objectAtIndex:0];
    if (workflow != nil)
    {
        [workflow touchWorkflowJobs];
        var workflowRunAsJson = {"workflow": [workflow pk], "creator": [activeUser pk]},
            workflowRun = [[WorkflowRun alloc] initWithJson:workflowRunAsJson];
        [workflowRun ensureCreated];
    }
}


/**
 * Tests the workflow.
 */
- (@action)testWorkflow:(id)aSender
{
    var workflow = [WorkflowController activeWorkflow];
    if (workflow != nil)
    {
        [workflow touchWorkflowJobs];
        var selectedPage = [[workflowPagesArrayController contentArray] objectAtIndex:[workflowPagesArrayController selectionIndex]],
            workflowRunAsJson = {"workflow": [workflow pk], "test_run": true, "creator": [activeUser pk]},
            testWorkflowRun = [[WorkflowRun alloc] initWithJson:workflowRunAsJson];
        [testWorkflowRun setTestPageID:[selectedPage pk]];
        [testWorkflowRun ensureCreated];
    }
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)receiveHasFocusEvent:(CPNotification)aNotification
{
    [RKNotificationTimer setTimedNotification:_msLOADINTERVAL
                         notification:RodanShouldLoadWorkflowResultsWorkflowsNotification];
}


/**
 * Handles load notification and delegates loading to the associated sub-delegates.
 */
- (void)handleShouldLoadNotification:(CPNotification)aNotification
{
    // We need to refresh the known workflows.
    //...

    // Next, tell the workflow status delegate to update the currently selected workflow.
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowResultsWorkflowRunsNotification
                                          object:nil];

    // Finally, tell the runs status delegate to update.
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowResultsWorkflowResultsNotification
                                          object:nil];
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
}
@end
