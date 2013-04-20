@import <LPKit/LPMultiLineTextField.j>

@import "../Models/Page.j"
@import "../Models/WorkflowJobSetting.j"

@global activeUser
@global RodanShouldLoadWorkflowDesignerNotification
@global RodanDidLoadWorkflowNotification
@global RodanRemoveJobFromWorkflowNotification

JobItemType = @"JobItemType";
activeWorkflow = nil;

@implementation WorkflowDesignerController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;

    @outlet     CPTableView             currentWorkflow;
    @outlet     CPArrayController       currentWorkflowArrayController;
    @outlet     CPArrayController       workflowPagesArrayController;

    @outlet     CPWindow                addPagesToWorkflowWindow;
    @outlet     CPButton                addPagesToWorkflowButton;
    @outlet     CPTableView             addPagesToWorkflowTableView;

    @outlet     LoadActiveWorkflowDelegate loadActiveWorkflowDelegate;

    @outlet     CPTableView             jobList;

    @outlet     TNTabView               pageRunTabView;

    @outlet     CPView                  pageTab;
    @outlet     CPTableView             pageList;
    @outlet     CPArrayController       pageArrayController;
    @outlet     CPView                  pageThumbnailView;
    @outlet     CPButtonBar             pageListAddRemoveButtonBar;

    @outlet     CPView                  runTab;
    @outlet     CPTableView             runList;
    @outlet     CPArrayController       runArrayController;
    @outlet     CPButtonBar             runAddRemoveButtonBar;

    @outlet     TNTabView               workflowJobTabView;
    @outlet     CPView                  selectedWorkflowJobSettingsTab;
    @outlet     CPView                  selectedWorkflowJobDescriptionTab;
    @outlet     LPMultiLineTextField    selectedWorkflowJobDescription;

}

- (void)awakeFromCib
{
    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(shouldLoadWorkflow:)
                                          name:RodanShouldLoadWorkflowDesignerNotification
                                          object:nil];

    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(removeJobFromWorkflow:)
                                          name:RodanRemoveJobFromWorkflowNotification
                                          object:nil];


    [jobList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [pageList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [runList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    // [currentWorkflow setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [currentWorkflow setGridStyleMask:CPTableViewSolidHorizontalGridLineMask];
    [currentWorkflow registerForDraggedTypes:[JobItemType]];

    // page and run tab view
    var tab1 = [[CPTabViewItem alloc] initWithIdentifier:@"pageListTab"],
        tab2 = [[CPTabViewItem alloc] initWithIdentifier:@"runListTab"];
    [tab1 setLabel:@"Pages"];
    [tab1 setView:pageTab];

    [tab2 setLabel:@"Runs"];
    [tab2 setView:runTab];

    [pageRunTabView addTabViewItem:tab1];
    [pageRunTabView addTabViewItem:tab2];

    var addButton = [CPButtonBar plusPopupButton],
        removeButton = [CPButtonBar minusButton],
        addPagesTitle = @"Add Pages to Workflow...";
    [addButton addItemsWithTitles:[addPagesTitle]];

    var addPagesItem = [addButton itemWithTitle:addPagesTitle];
    [pageListAddRemoveButtonBar setButtons:[addButton, removeButton]];

    [addPagesItem setAction:@selector(openAddPagesWindow:)];
    [addPagesItem setTarget:self];

    [removeButton setAction:@selector(removePagesFromWorkflow:)];
    [removeButton setTarget:self];

    [removeButton bind:@"enabled"
                  toObject:workflowPagesArrayController
                  withKeyPath:@"selection.pk"
                  options:nil];

    // [removeButton bind:@""]

    // Inspector Pane
    var tab1 = [[CPTabViewItem alloc] initWithIdentifier:@"settingsTab"],
        tab2 = [[CPTabViewItem alloc] initWithIdentifier:@"descriptionTab"];
    [tab1 setLabel:@"Settings"];
    [tab1 setView:selectedWorkflowJobSettingsTab];
    [tab2 setLabel:@"Description"];
    [tab2 setView:selectedWorkflowJobDescriptionTab];
    [workflowJobTabView addTabViewItem:tab1];
    [workflowJobTabView addTabViewItem:tab2];

    [selectedWorkflowJobDescription bind:@"value"
                                    toObject:currentWorkflowArrayController
                                    withKeyPath:@"selection.jobDescription"
                                    options:nil];
}

- (void)shouldLoadWorkflow:(CPNotification)aNotification
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[[aNotification object] pk]
                    delegate:loadActiveWorkflowDelegate
                    message:"Loading Workflow Jobs"];

}

- (@action)selectWorkflow:(id)aSender
{
    var selectedWorkflow = [[workflowArrayController selectedObjects] objectAtIndex:0];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowDesignerNotification
                                          object:selectedWorkflow];
}

- (@action)removeJobFromWorkflow:(CPNotification)aSender
{
    [currentWorkflowArrayController removeObject:[[aSender object] objectValue]];
    [[[aSender object] objectValue] ensureDeleted];
}

- (@action)removePagesFromWorkflow:(id)aSender
{
    //pass
}

- (@action)openAddPagesWindow:(id)aSender
{
    // [addImagesToWorkflowWindow makeKeyAndOrderFront:aSender];
    [addPagesToWorkflowWindow setDefaultButton:addPagesToWorkflowButton];
    [CPApp beginSheet:addPagesToWorkflowWindow
           modalForWindow:[CPApp mainWindow]
           modalDelegate:self
           didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (@action)closeAddPagesSheet:(id)aSender
{
    if ([aSender tag] === 0)
    {
        var myObjects = [pageArrayController selectedObjects];
        [workflowPagesArrayController addObjects:myObjects];
    }

    [CPApp endSheet:addPagesToWorkflowWindow returnCode:[aSender tag]];
}

- (void)didEndSheet:(CPWindow)aSheet returnCode:(int)returnCode contextInfo:(id)contextInfo
{
    [addPagesToWorkflowWindow orderOut:self];
}

- (@action)testWorkflow:(id)aSender
{
    // this forces the workflow jobs to update themselves to the server
    [[activeWorkflow workflowJobs] makeObjectsPerformSelector:@selector(makeAllDirty)];
    [[activeWorkflow workflowJobs] makeObjectsPerformSelector:@selector(ensureSaved)];

    var selectedPage = [[workflowPagesArrayController contentArray] objectAtIndex:[workflowPagesArrayController selectionIndex]],
        workflowRun = {
        "workflow": [activeWorkflow pk],
        "test_run": true,
        "creator": [activeUser pk]
        },
        testWorkflowRun = [[WorkflowRun alloc] initWithJson:workflowRun];
    [testWorkflowRun setTestPageID:[selectedPage pk]];
    [testWorkflowRun ensureCreated];
}

- (@action)runWorkflow:(id)aSender
{
    // this forces the workflow jobs to update themselves to the server
    [[activeWorkflow workflowJobs] makeObjectsPerformSelector:@selector(makeAllDirty)];
    [[activeWorkflow workflowJobs] makeObjectsPerformSelector:@selector(ensureSaved)];

    var workflowRunObj = {
        "workflow": [activeWorkflow pk],
        "creator": [activeUser pk]
        },
        workflow = [[WorkflowRun alloc] initWithJson:workflowRunObj];
    [workflow ensureCreated];
}

@end


@implementation WorkflowDesignerDelegate : CPObject
{
    @outlet     CPTableView         currentWorkflow;
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   jobArrayController;
}

- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    return [[currentWorkflowArrayController contentArray] count];
}

- (void)tableViewDeleteKeyPressed:(CPTableView)aTableView
{
    var deletedObjects = [currentWorkflowArrayController selectedObjects];
    [WLRemoteObject setDirtProof:YES];
    [currentWorkflowArrayController removeObjects:deletedObjects];
    [WLRemoteObject setDirtProof:NO];
    [deletedObjects makeObjectsPerformSelector:@selector(removeFromWorkflow)];
}

- (void)tableView:(CPTableView)aTableView viewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    return [aTableView makeViewWithIdentifier:@"workflowJob" owner:self];
}

- (CPDragOperation)tableView:(CPTableView)aTableView
                   validateDrop:(id)info
                   proposedRow:(CPInteger)row
                   proposedDropOperation:(CPTableViewDropOperation)operation
{
    [currentWorkflow setDropRow:row dropOperation:CPTableViewDropAbove];
    return CPDragOperationCopy;
}

- (void)tableView:(CPTableView)aTableView willDisplayView:(id)aView forTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
}

- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)anIndex dropOperation:(CPTableViewDropOperation)aDropOperation
{
    var content = [jobArrayController contentArray],
        pboard = [info draggingPasteboard],
        sourceIndexes = [pboard dataForType:JobItemType],
        jobObj = [content objectAtIndex:[sourceIndexes firstIndex]];

    var inputTypes = JSON.parse([jobObj inputTypes]),
        outputTypes = JSON.parse([jobObj outputTypes]);

    // Check to see if this job can fit in with the next or previous ones
    var inputPixelTypes = [CPSet setWithArray:inputTypes.pixel_types],
        outputPixelTypes = [CPSet setWithArray:outputTypes.pixel_types],
        inputTypePasses = NO,
        outputTypePasses = NO,
        contentArrayCount = [[currentWorkflowArrayController contentArray] count];

    if (contentArrayCount === 0)
    {
        inputTypePasses = YES;
        outputTypePasses = YES;
    }
    else
    {
        var lastIndex = contentArrayCount - 1,
            prevObject,
            nextObject;

        // console.log("An Index: " + anIndex);
        // console.log("last index: " + lastIndex);
        if (anIndex === 0)
        {
            // console.log("inserting at beginning");
            nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];

            inputTypePasses = YES;
            outputTypePasses = [self _checkOutputTypeMatches:nextObject withPixelTypes:outputPixelTypes];
        }
        else if (anIndex === contentArrayCount)
        {
            // console.log("Inserting at end");
            prevObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1];

            inputTypePasses = [self _checkInputTypeMatches:prevObject withPixelTypes:inputPixelTypes];
            outputTypePasses = YES;
        }
        else
        {
            // console.log("Inserting somewhere in the middle");
            // if we're inserting in the middle, the next object is the one we're looking for.
            prevObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1];
            nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];

            inputTypePasses = [self _checkInputTypeMatches:prevObject withPixelTypes:inputPixelTypes];
            outputTypePasses = [self _checkOutputTypeMatches:nextObject withPixelTypes:outputPixelTypes];
        }
    }

    // do not permit a drop if either the input or the output passes
    if (!inputTypePasses || !outputTypePasses)
        return NO;

    var interactive = false,
        needsInput = false,
        jobType = 0;

    if ([jobObj isInteractive])
    {
        interactive = true;
        needsInput = true;
        jobType = 1;
    }

    // create a workflow job JSON object for this new job.
    var wkObj = {
            "workflow": [activeWorkflow pk],
            "job": [jobObj pk],
            "job_name": [jobObj jobName],
            "job_settings": [jobObj settings],
            "job_type": jobType,
            "interactive": interactive,
            "needs_input": needsInput
            },
        workflowJobObject = [[WorkflowJob alloc] initWithJson:wkObj];
    [workflowJobObject ensureCreated];

    /// don't send a patch request for updating this array
    [WLRemoteObject setDirtProof:YES];
    [[currentWorkflowArrayController contentArray] insertObject:workflowJobObject atIndex:anIndex];

    // update the workflow jobs sequence property
    [[currentWorkflowArrayController contentArray] enumerateObjectsUsingBlock:function(obj, idx, stop)
        {
            [obj setSequence:idx + 1];  // sequence in a workflow is 1-based;
        }];
    [WLRemoteObject setDirtProof:NO];

    return YES;
}

/***
    Checks if a job's pixel types match the input type of another job object.
***/
- (BOOL)_checkInputTypeMatches:(id)anObject withPixelTypes:(CPSet)pixelTypes
{
    var prevObjJobId = [anObject job],
        prevJobIdx = [[jobArrayController contentArray] indexOfObjectPassingTest:function(obj, idx)
            {
                return [obj pk] === prevObjJobId;
            }],
        previousJob = [[jobArrayController contentArray] objectAtIndex:prevJobIdx],
        prevOutputTypes = JSON.parse([previousJob outputTypes]),
        prevOutputSet = [CPSet setWithArray:prevOutputTypes.pixel_types];

    if ([prevOutputSet intersectsSet:pixelTypes])
        return YES;
    else
        return NO;
}

/***
    Checks if a job's pixel types match the output type of another job object.
***/
- (BOOL)_checkOutputTypeMatches:(id)anObject withPixelTypes:(CPSet)pixelTypes
{
    console.log("An object: ");
    console.log(anObject);

    var nextObjJobId = [anObject job],
        nextJobIdx = [[jobArrayController contentArray] indexOfObjectPassingTest:function(obj, idx)
        {
            return [obj pk] == nextObjJobId;
        }],
        nextJob = [[jobArrayController contentArray] objectAtIndex:nextJobIdx],
        nextInputTypes = JSON.parse([nextJob inputTypes]),
        nextInputSet = [CPSet setWithArray:nextInputTypes.pixel_types];

    if ([nextInputSet intersectsSet:pixelTypes])
        return YES;
    else
        return NO;
}

@end


/***
    A delegate method for loading the remote workflow from the server.
***/
@implementation LoadActiveWorkflowDelegate : CPObject
{
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   workflowPagesArrayController;
    @outlet     CPArrayController   workflowRunsArrayController;
}
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    // since we're initializing another model for this workflow object,
    // we don't want it to sync back to the server when we create it.
    // so we set it as "Dirt Proof" while it's being created.
    [WLRemoteObject setDirtProof:YES];
    activeWorkflow = [[Workflow alloc] initWithJson:[anAction result]];
    [WLRemoteObject setDirtProof:NO];

    [currentWorkflowArrayController bind:@"contentArray"
                                    toObject:activeWorkflow
                                    withKeyPath:@"workflowJobs"
                                    options:nil];

    [workflowPagesArrayController bind:@"contentArray"
                                  toObject:activeWorkflow
                                  withKeyPath:@"pages"
                                  options:nil];

    [workflowRunsArrayController bind:@"contentArray"
                                 toObject:activeWorkflow
                                 withKeyPath:@"workflowRuns"
                                 options:nil];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowNotification
                                          object:nil];
}

@end


/***
    A simple class that handles some of the delegate methods to support drag-n-drop.
***/
@implementation JobListDelegate : CPObject
{
}

- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    // needed so that it doesn't complain about not having the delegate function.
}

- (BOOL)tableView:(CPTableView)aTableView writeRowsWithIndexes:(CPIndexSet)rowIndexes toPasteboard:(CPPasteboard)pboard
{
    console.log("write rows with indexes");
    [pboard declareTypes:[JobItemType] owner:self];
    [pboard setData:rowIndexes forType:JobItemType];

    return YES;
}

@end

@implementation PageListDelegate : CPObject
{
    @outlet     CPArrayController       pageArrayController;
}

- (void)tableView:(CPTableView)aTableView viewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    var aView = [aTableView makeViewWithIdentifier:@"workflowPage" owner:self];

    return aView;
}

@end

@implementation PageListCellView : CPView
{
    id          objectValue @accessors;
    CPTextField textField   @accessors;
}

- (id)init
{
    self = [super init];
    return self;
}

- (id)initWithFrame:(CGRect)aFrame
{
    self = [super initWithFrame:aFrame];
    return self;
}

- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder];
    return self;
}

- (void)setObjectValue:(id)aValue
{
    objectValue = aValue;
}

@end

