@import <Foundation/CPObject.j>
@import <AppKit/CPArrayController.j>
@import <AppKit/CPBrowser.j>
@import <AppKit/CPOutlineView.j>
@import <AppKit/CPTableView.j>

@import "../Models/Workflow.j"
@import "../Models/WorkflowJob.j"

@global activeProject;
@global RodanDidLoadWorkflowsNotification;
@global RodanWorkflowTreeNeedsRefresh;

@implementation WorkflowController : CPObject
{
    @outlet     CPBrowser           jobBrowser;
    @outlet     CPTableView         existingWorkflows;
    @outlet     CPTableView         availableJobs;
    AvailableJobTableDelegate       availableJobDelegate;

    @outlet     CPTableView         workflowView;
    @outlet     CPArrayController   workflowArrayController;

                CPImage             workflowIcon;
}

- (void)fetchWorkflows
{
    [WLRemoteAction schedule:WLRemoteActionGetType path:"/workflows" delegate:self message:"Loading jobs"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    if ([anAction result])
    {
        console.log([anAction result]);
        var j = [Workflow objectsFromJson:[anAction result]];
        [workflowArrayController addObjects:j];
        [existingWorkflows setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
        [availableJobs setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
        // availableJobDelegate = [[AvailableJobTableDelegate alloc] init];
        // [availableJobs setDelegate:availableJobDelegate];

        [workflowView registerForDraggedTypes:["JobType"]];

        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowsNotification
                                              object:[anAction result]];
    }
}

- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (IBAction)saveWorkflow:(id)aSender
{
    CPLog("Save Workflow");
}

- (IBAction)addImagesToWorkflow:(id)aSender
{
    CPLog("Add Image to Workflow");
}

- (IBAction)editWorkflow:(id)aSender
{
    CPLog("Edit Workflow");
}

- (IBAction)startWorkflow:(id)aSender
{
    CPLog("Start Workflow");
    var selectedObjects = [workflowArrayController selectedObjects];
    console.log(selectedObjects);
}


- (IBAction)stopWorkflow:(id)aSender
{
    CPLog("Stop Workflow");
}

- (IBAction)loadJobsForWorkflow:(id)aSender
{
    var selectionIndex = [workflowArrayController selectionIndex];
    console.log(selectionIndex);
    if (selectionIndex != -1)
    {
        var workflow = [[workflowArrayController contentArray] objectAtIndex:selectionIndex];

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
    [wflow setProjectURI:[activeProject pk]];
    [workflowArrayController addObject:wflow];
    [wflow ensureCreated];
}

- (void)newWorkflowGroup:(id)aSender
{
    CPLog("In the workflow controller");
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

@implementation AvailableJobTableDelegate : CPObject
{

}

- (id)init
{
    if (self = [super init])
    {

    }

    return self;
}

- (BOOL)tableView:(CPTableView)aTableView writeRowsWithIndexes:(CPIndexSet)rowIndexes toPasteboard:(CPPasteboard)pboard
{
    console.log("Starting Drag");
    var data = [CPKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[CPArray arrayWithObject:@"JobType"] owner:self];
    [pboard setData:data forType:@"JobType"];
    return YES;
}

- (void)pasteboard:(CPPasteboard)pboard provideDataForType:(CPString)aType
{
    console.log("Provide data for type");
}

@end

@implementation WorkflowDesignerDelegate : CPObject
{
    @outlet     CPArrayController   workflowDesignerArrayController;
    @outlet     CPArrayController   jobArrayController;
}

- (id)init
{
    if (self = [super init])
    {

    }

    return self;
}

- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)row dropOperation:(CPTableViewDropOperation)operation
{
    console.log("Checking can accept drop");
    var pboard = [info draggingPasteboard],
        rowData = [pboard dataForType:@"JobType"],
        dragRows = [CPKeyedUnarchiver unarchiveObjectWithData:rowData],
        rowIdx = [dragRows firstIndex],
        jobObj = [[jobArrayController contentArray] objectAtIndex:rowIdx];

    console.log(jobObj);

    var wJob = [[WorkflowJob alloc] init];

    [wJob setJobName:[jobObj jobName]];

    [workflowDesignerArrayController addObject:wJob];

    // [aTableView reloadData];

    return YES;
}

- (CPDragOperation)tableView:(CPTableView)aTableView
                   validateDrop:(id)info
                   proposedRow:(CPInteger)row
                   proposedDropOperation:(CPTableViewDropOperation)operation
{
/*    if (aTableView === tableView)
        [aTableView setDropRow:row dropOperation:CPTableViewDropOn];
    else
        [aTableView setDropRow:row dropOperation:CPTableViewDropAbove];
*/
    // console.log("Validated Drop");
    [aTableView setDropRow:row dropOperation:CPTableViewDropAbove];
    return CPDragOperationCopy;
}

- (int)numberOfRowsInTable:(id)tableView
{
    console.log("Num rows in table");
    return [workflowDesignerArrayController count];
}

@end

