@global RodanShouldLoadWorkflowDesignerNotification
@global RodanRemoveJobFromWorkflowNotification
@global RodanDidLoadWorkflowNotification

JobItemType = @"JobItemType";
activeWorkflow = nil;

@implementation WorkflowDesignerController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
    @outlet     CPArrayController       currentWorkflowArrayController;
    @outlet     CPObject                activeWorkflowDelegate;
    @outlet     CPTableView             jobList;
    @outlet     CPTextField             jobInfo;
    @outlet     CPTableView             currentWorkflow;
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
    // [currentWorkflow setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [currentWorkflow setGridStyleMask:CPTableViewSolidHorizontalGridLineMask];
    [currentWorkflow registerForDraggedTypes:[CPArray arrayWithObject:JobItemType]];
}

- (void)shouldLoadWorkflow:(CPNotification)aNotification
{
    console.log("I should load the jobs for workflow " + [activeWorkflow pk]);
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[activeWorkflow pk]
                    delegate:activeWorkflowDelegate
                    message:"Loading Workflow Jobs"];

}

- (IBAction)selectWorkflow:(id)aSender
{
    activeWorkflow = [[workflowArrayController selectedObjects] objectAtIndex:0];

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowDesignerNotification
                                          object:nil];
}

- (IBAction)removeJobFromWorkflow:(CPNotification)aSender
{
    [currentWorkflowArrayController removeObject:[[aSender object] objectValue]];
    [[[aSender object] objectValue] ensureDeleted];
}

@end

@implementation LoadActiveWorkflowDelegate : CPObject
{
    @outlet     CPArrayController   currentWorkflowArrayController;
}
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    console.log("Remote action did finish");

    var workflowJobs = [WorkflowJob objectsFromJson:[anAction result].wjobs];
    [currentWorkflowArrayController addObjects:workflowJobs];

    console.log(currentWorkflowArrayController);

    [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadWorkflowNotification
                                          object:nil];
}

@end


@implementation WorkflowDesignerDelegate : CPObject
{
    @outlet     CPTableView         currentWorkflow;
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   jobArrayController;

    @outlet     CPView              workflowJobView;
}

- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    return [[currentWorkflowArrayController contentArray] count];
}

// - (void)tableView:(CPTableView)aTableView dataViewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
// {
//     // console.log("Data view for table column");
//     var identifier = [aTableColumn identifier],
//         aView = [aTableView makeViewWithIdentifier:@"workflowJob" owner:self];

//     return aView;
// }

- (@action)didSelectRow:(id)aSender
{
    console.log("Did select row");
    console.log([currentWorkflowArrayController selectionIndex]);
}

// - (void)tableView:(CPTableView)aTableView willDisplayView:(CPView)aView forTableColumn:(CPTableColumn)aColumn row:(int)aRow
// {
//     // console.log('will display view');
// }

- (void)tableViewDeleteKeyPressed:(CPTableView)aTableView
{
    var deletedObjects = [currentWorkflowArrayController selectedObjects];
    [currentWorkflowArrayController removeObjects:deletedObjects];
    [deletedObjects makeObjectsPerformSelector:@selector(ensureDeleted)];
}

- (CPDragOperation)tableView:(CPTableView)aTableView
                   validateDrop:(id)info
                   proposedRow:(CPInteger)row
                   proposedDropOperation:(CPTableViewDropOperation)operation
{
    // console.log("Validate Drop");
    [currentWorkflow setDropRow:row dropOperation:CPTableViewDropAbove];

    return CPDragOperationCopy;
}

- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)anIndex dropOperation:(CPTableViewDropOperation)aDropOperation
{
    // console.log("accept drop?");
    var content = [jobArrayController contentArray],
        pboard = [info draggingPasteboard],
        sourceIndexes = [pboard dataForType:JobItemType],
        jobObj = [content objectAtIndex:[sourceIndexes firstIndex]];

    var input_types = JSON.parse([jobObj inputTypes]),
        output_types = JSON.parse([jobObj outputTypes]);

    // Check to see if this job can fit in with the next or previous ones
    var inputPixelTypes = [CPSet setWithArray:input_types.pixel_types],
        outputPixelTypes = [CPSet setWithArray:output_types.pixel_types],
        input_type_passes = NO,
        output_type_passes = NO,
        contentArrayCount = [[currentWorkflowArrayController contentArray] count];

    if (contentArrayCount === 0)
    {
        input_type_passes = YES;
        output_type_passes = YES;
    }
    else
    {
        var lastIndex = contentArrayCount - 1,
            prevObject,
            nextObject;

        console.log("An Index: " + anIndex);
        console.log("last index: " + lastIndex);
        if (anIndex === 0)
        {
            console.log("inserting at beginning");
            nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];

            input_type_passes = YES;
            output_type_passes = [self _checkOutputTypeMatches:nextObject withPixelTypes:outputPixelTypes];
        }
        else if (anIndex === contentArrayCount)
        {
            console.log("Inserting at end");
            prevObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1];

            input_type_passes = [self _checkInputTypeMatches:prevObject withPixelTypes:inputPixelTypes];
            output_type_passes = YES;
        }
        else
        {
            console.log("Inserting somewhere in the middle");
            // if we're inserting in the middle, the next object is the one we're looking for.
            prevObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1];
            nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];

            input_type_passes = [self _checkInputTypeMatches:prevObject withPixelTypes:inputPixelTypes];
            output_type_passes = [self _checkOutputTypeMatches:nextObject withPixelTypes:outputPixelTypes];
        }
    }

    // do not permit a drop if either the input or the output passes
    if (!input_type_passes || !output_type_passes)
    {
        return NO;
    }

    // The JSON field module we're using likes setting an empty dictionary
    // as a placeholder for fields with no values. We always want to have
    // this set as an array, even if it is blank.
    // if ([jobObj arguments] === "{}")
    //     var jobSettings = "[{}]";
    // else
    //     var jobSettings = [jobObj arguments];

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
            "job_settings": [jobObj arguments],
            "sequence": anIndex,
            "job_type": jobType,
            "interactive": interactive,
            "needs_input": needsInput
            };

    // console.log(wkObj);

    var workflowJobObject = [[WorkflowJob alloc] initWithJson:wkObj];
    [workflowJobObject ensureCreated];

    [currentWorkflowArrayController insertObject:workflowJobObject atArrangedObjectIndex:anIndex];

    return YES;
}

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
    {
        console.log("Previous Job Pixel output: ");
        console.log(prevOutputSet);
        console.log("This pixel type: ");
        console.log(pixelTypes);
        return YES;
    }
    else
    {
        console.log('input type does not match');
        return NO;
    }
}

- (BOOL)_checkOutputTypeMatches:(id)anObject withPixelTypes:(CPSet)pixelTypes
{
    var nextObjJobId = [anObject job],
        nextJobIdx = [[jobArrayController contentArray] indexOfObjectPassingTest:function(obj, idx)
        {
            return [obj pk] == nextObjJobId;
        }],
        nextJob = [[jobArrayController contentArray] objectAtIndex:nextJobIdx],
        nextInputTypes = JSON.parse([nextJob inputTypes]),
        nextInputSet = [CPSet setWithArray:nextInputTypes.pixel_types];

    if ([nextInputSet intersectsSet:pixelTypes])
    {
        console.log("Previous Job Pixel output: ");
        console.log(nextInputSet);
        console.log("This pixel type: ");
        console.log(pixelTypes);
        return YES;
    }
    else
    {
        console.log("output type does not match");
        return NO;
    }
}

@end

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
    [pboard declareTypes:[CPArray arrayWithObject:JobItemType] owner:self];
    [pboard setData:rowIndexes forType:JobItemType];

    return YES;
}

@end

// @implementation WorkflowJobView : CPTableCellView
// {
//                 id          objectValue     @accessors;
//     @outlet     CPTextField jobName         @accessors;
//                 CPArray     jobSettings     @accessors;
//                 int         viewHeight      @accessors;
// }

// // if an object has keys, return false; otherwise it's empty.
// - (BOOL)_isEmptyObject:(id)anObject
// {
//     for (var i in anObject)
//     {
//         return false;
//     }
//     return true;
// }

// - (void)setObjectValue:(id)aValue
// {
//     // console.log("Setting object value");
//     // console.log(aValue);
//     objectValue = aValue;

//     // var topOrigin = 25,
//     //     leftOrigin = 25,
//     //     widgetHeight = 25,
//     //     widgetWidth = 100,
//     //     labelWidth = 300;


//     // jobSettings = [CPArray arrayWithArray:JSON.parse([aValue jobSettings])];
//     // var prevWidget = nil;

//     // viewHeight = 50;

//     // for (var i = 0; i < [jobSettings count]; i++)
//     // {
//     //     var widget,
//     //         label,
//     //         labelString = @"",
//     //         obj = [jobSettings objectAtIndex:i];

//     //     if ([self _isEmptyObject:obj])
//     //         continue;

//     //     if (obj.type == "imagetype")
//     //         continue;

//     //     label = [[CPTextField alloc] initWithFrame:CGRectMake(leftOrigin + widgetWidth + 5, topOrigin, labelWidth, widgetHeight)];

//     //     if (obj.name)
//     //         labelString = [CPString stringWithString:obj.name];
//     //     else
//     //         labelString = @"No name";

//     //     if (obj.type === "int" || obj.type === "real" || obj.type === "pixel")
//     //     {
//     //         widget = [[CPTextField alloc] initWithFrame:CGRectMake(leftOrigin, topOrigin, widgetWidth, widgetHeight)];
//     //         [widget setEditable:YES];
//     //         [widget setBezeled:YES];

//     //         if (obj.has_default)
//     //             [widget setObjectValue:obj.default];

//     //         if (obj.rng)
//     //         {
//     //             var lowerBounds = obj.rng[0],
//     //                 upperBounds = obj.rng[1],
//     //                 formatter = [[CPNumberFormatter alloc] init];

//     //             labelString = [labelString stringByAppendingFormat:@" (min: %d, max: %d)", lowerBounds, upperBounds];

//     //             [formatter setMinimum:lowerBounds];
//     //             [formatter setMaximum:upperBounds];
//     //             [widget setFormatter:formatter];
//     //         }
//     //     }
//     //     else if (obj.type === "choice")
//     //     {
//     //         var widget = [[CPPopUpButton alloc] initWithFrame:CGRectMake(leftOrigin, topOrigin, widgetWidth, widgetHeight)];
//     //         [widget addItemsWithTitles:[CPArray arrayWithArray:obj.choices]];
//     //     }

//     //     [self addSubview:widget];
//     //     [label setObjectValue:labelString];
//     //     [self addSubview:label];

//     //     prevWidget = widget;
//     //     topOrigin += widgetHeight + 5;  // add 5 pixels spacing between fields

//     //     viewHeight += 30;
//     // }
// }

// - (void)drawRect:(CGRect)aRect
// {
//     var context = [[CPGraphicsContext currentContext] graphicsPort];
//     CGContextSetFillColor(context, [CPColor grayColor]);
//     CGContextFillRoundedRectangleInRect(context, [self bounds], 6.0, 6.0, YES, YES, YES, YES);
// }

// - (@action)removeSelfFromWorkflow:(id)aSender
// {
//     [[CPNotificationCenter defaultCenter] postNotificationName:RodanRemoveJobFromWorkflowNotification
//                                       object:self];

// }

// @end
