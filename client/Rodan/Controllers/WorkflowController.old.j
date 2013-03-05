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
    @outlet     CPTableView         existingWorkflows;
    @outlet     CPTableView         availableJobs;
    AvailableJobTableDelegate       availableJobDelegate;

    @outlet     CPCollectionView    workflowView;
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
        [availableJobs setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];

        var workflowCollectionDelegate = [[WorkflowDesignerDelegate alloc] init];
        [workflowView setDelegate:workflowCollectionDelegate];
        [workflowView registerForDraggedTypes:["JobType"]];
        var bounds = [workflowView bounds];

        [workflowView setMinItemSize:CGSizeMake(bounds.size.width - 20, 80)];
        [workflowView setMaxItemSize:CGSizeMake(bounds.size.width - 20, 80)];
        var bgImg = [[CPImage alloc] initWithContentsOfFile:[[CPBundle mainBundle] pathForResource:@"denim.png"]
                                     size:CGSizeMake(135, 135)];

        [workflowView setBackgroundColor:[CPColor colorWithPatternImage:bgImg]];

        var carr = [[CPMutableArray alloc] init];
        for (var i = 100; i >= 0; i--)
        {
            [carr addObject:{"id": i}];
        };
        [workflowView setContent:carr];

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

- (int)numberOfRowsInTableView:(id)aTableView
{
    //pass
}

@end


@implementation WorkflowDesignerDelegate : CPObject
{

}

- (CPData)collectionView:(CPCollectionView)aCollectionView dataForItemsAtIndexes:(CPIndexSet)indices forType:(CPString)aType
{
    console.log("Col view dataForItemsAtIndexes");
}

- (CPArray)collectionView:(CPCollectionView)aCollectionView dragTypesForItemsAtIndexes:(CPIndexSet)indices
{
    return [@"JobType"];
}

- (void)collectionViewDidChangeSelection:(CPCollectionView)collectionView
{
    console.log("Changed selection");
}

@end


@implementation JobItemView : CPView
{
}

- (id)initWithFrame:(CPRect)aFrame
{
    self = [super initWithFrame:aFrame];
    if (self)
    {
        console.log("Init With Frame");
    }
    return self;
}

- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder];
    if (self)
    {
        console.log("Init with Coder");
    }
    return self;
}

- (id)init
{
    if (self = [super init])
    {
        console.log("Regular Init");
    }
    return self;
}

- (IBAction)aClick:(id)aSender
{
    console.log("Clicked");
}

- (void)setRepresentedObject:(id)anObject
{
    [self setBackgroundColor:[CPColor whiteColor]];
    // console.log(anObject);
}

- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder];
    return self;
}

- (void)encodeWithCoder:(CPCoder)aCoder
{
    [super encodeWithCoder:aCoder];

}

@end
