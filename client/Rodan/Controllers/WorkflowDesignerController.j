@global RodanShouldLoadWorkflowDesignerNotification
@global RodanRemoveJobFromWorkflowNotification

JobItemType = @"JobItemType";
activeWorkflow = nil;

@implementation WorkflowDesignerController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
    @outlet     CPArrayController       currentWorkflowArrayController;
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


@implementation WorkflowDesignerDelegate : CPObject
{
    @outlet     CPTableView         currentWorkflow;
    @outlet     CPArrayController   currentWorkflowArrayController;
    @outlet     CPArrayController   jobArrayController;
                CPMutableArray      shadowWorkflowViewArray; // used so that we can keep track of the views

    @outlet     CPView              workflowJobView;
}

- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    return [[currentWorkflowArrayController contentArray] count];
}

- (void)tableView:(CPTableView)aTableView dataViewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    // console.log("Data view for table column");
    var identifier = [aTableColumn identifier],
        aView = [aTableView makeViewWithIdentifier:@"workflowJob" owner:self];

    return aView;
}

- (int)tableView:(CPTableView)aTableView heightOfRow:(int)aRow
{
    // create a dummy table cell view with the value of the row
    // for calculating the view height. This is a hack until we get
    // proper querying of the view in the table.
    console.log("For row: ");
    console.log(aRow);
    var tmpCell = [[WorkflowJobView alloc] init],
        tmpValue = [[currentWorkflowArrayController contentArray] objectAtIndex:aRow];
    [tmpCell setObjectValue:tmpValue];

    var height = [tmpCell viewHeight];

    [aTableView setRowHeight:height];

    tmpCell = nil;
    tmpValue = nil;

    return height;
}

- (void)tableView:(CPTableView)aTableView willDisplayView:(CPView)aView forTableColumn:(CPTableColumn)aColumn row:(int)aRow
{
    console.log('will display view');
}

- (CPDragOperation)tableView:(CPTableView)aTableView
                   validateDrop:(id)info
                   proposedRow:(CPInteger)row
                   proposedDropOperation:(CPTableViewDropOperation)operation
{
    console.log("Validate Drop");
    [currentWorkflow setDropRow:row dropOperation:CPTableViewDropAbove];

    return CPDragOperationCopy;
}

- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)anIndex dropOperation:(CPTableViewDropOperation)aDropOperation
{
    console.log("accept drop?");
    var content = [jobArrayController contentArray],
        pboard = [info draggingPasteboard],
        sourceIndexes = [pboard dataForType:JobItemType],
        jobObj = [content objectAtIndex:[sourceIndexes firstIndex]];

    var input_types = JSON.parse([jobObj inputTypes]),
        output_types = JSON.parse([jobObj outputTypes]);

    // Check to see if this job can fit in with the next or previous ones
    var input_pixel_types = [CPSet setWithArray:input_types.pixel_types],
        output_pixel_types = [CPSet setWithArray:output_types.pixel_types],
        input_type_passes = NO,
        output_type_passes = NO;

    if ([[currentWorkflowArrayController contentArray] count] === 0)
    {
        // we can't fail because we don't have anything to check against
        // console.log("Empty content array");
        input_type_passes = YES;
        output_type_passes = YES;
    }
    else
    {
        // check the previous item in the content array
        if (anIndex === 0)  // we're trying to insert it at the beginning
        {
            // console.log("At the beginning?");
            input_type_passes = YES;
        }
        else
        {
            var previousObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1],
                prevObjJobId = [previousObject job];

            var prevJobIdx = [[jobArrayController contentArray] indexOfObjectPassingTest:function(obj, idx)
                {
                    return [obj pk] == prevObjJobId;
                }];

            var previousJob = [[jobArrayController contentArray] objectAtIndex:prevJobIdx],
                prevOutputTypes = JSON.parse([previousJob outputTypes]),
                prevOutputSet = [CPSet setWithArray:prevOutputTypes.pixel_types];

            // console.log("Previous Job");
            // console.log(prevOutputSet);
            // console.log("This Job");
            // console.log(input_pixel_types);

            if ([prevOutputSet intersectsSet:input_pixel_types])
                input_type_passes = YES;
        }

        if (anIndex == [[currentWorkflowArrayController contentArray] count])
        {
            // we're appending to the end, so the output type should pass
            // console.log("At the end?");
            output_type_passes = YES;
        }
        else
        {
            if (anIndex === 0)
                /*
                    If we we're here and anIndex is 0, it means we're inserting
                    a job at the beginning of the workflow. This will shift the
                    existing jobs down, but we need to get the first object in the array.
                */
                var nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];
            else
                var nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex + 1];

            var nextObjJobId = [nextObject job],
                nextJobIdx = [[jobArrayController contentArray] indexOfObjectPassingTest:function(obj, idx)
                {
                    return [obj pk] == nextObjJobId;
                }];

            var nextJob = [[jobArrayController contentArray] objectAtIndex:nextJobIdx],
                nextInputTypes = JSON.parse([nextJob inputTypes]),
                nextInputSet = [CPSet setWithArray:nextInputTypes.pixel_types];

            if ([nextInputSet intersectsSet:output_pixel_types])
                output_type_passes = YES;
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
    if ([jobObj arguments] === "{}")
        var jobSettings = "[{}]";
    else
        var jobSettings = [jobObj arguments];

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
            "job_settings": jobSettings,
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

@implementation WorkflowJobView : CPTableCellView
{
                id          objectValue     @accessors;
    @outlet     CPTextField jobName         @accessors;
                CPArray     jobSettings     @accessors;
                int         viewHeight      @accessors;
}

// if an object has keys, return false; otherwise it's empty.
- (BOOL)_isEmptyObject:(id)anObject
{
    for (var i in anObject)
    {
        return false;
    }
    return true;
}

- (void)setObjectValue:(id)aValue
{
    console.log("Setting object value");
    objectValue = aValue;

    var topOrigin = 25,
        leftOrigin = 25,
        widgetHeight = 25,
        widgetWidth = 100,
        labelWidth = 300;


    // jobSettings = [CPArray arrayWithArray:JSON.parse([aValue jobSettings])];
    var prevWidget = nil;

    viewHeight = 50;

    // for (var i = 0; i < [jobSettings count]; i++)
    // {
    //     var widget,
    //         label,
    //         labelString = @"",
    //         obj = [jobSettings objectAtIndex:i];

    //     if ([self _isEmptyObject:obj])
    //         continue;

    //     if (obj.type == "imagetype")
    //         continue;

    //     label = [[CPTextField alloc] initWithFrame:CGRectMake(leftOrigin + widgetWidth + 5, topOrigin, labelWidth, widgetHeight)];

    //     if (obj.name)
    //         labelString = [CPString stringWithString:obj.name];
    //     else
    //         labelString = @"No name";

    //     if (obj.type === "int" || obj.type === "real" || obj.type === "pixel")
    //     {
    //         widget = [[CPTextField alloc] initWithFrame:CGRectMake(leftOrigin, topOrigin, widgetWidth, widgetHeight)];
    //         [widget setEditable:YES];
    //         [widget setBezeled:YES];

    //         if (obj.has_default)
    //             [widget setObjectValue:obj.default];

    //         if (obj.rng)
    //         {
    //             var lowerBounds = obj.rng[0],
    //                 upperBounds = obj.rng[1],
    //                 formatter = [[CPNumberFormatter alloc] init];

    //             labelString = [labelString stringByAppendingFormat:@" (min: %d, max: %d)", lowerBounds, upperBounds];

    //             [formatter setMinimum:lowerBounds];
    //             [formatter setMaximum:upperBounds];
    //             [widget setFormatter:formatter];
    //         }
    //     }
    //     else if (obj.type === "choice")
    //     {
    //         var widget = [[CPPopUpButton alloc] initWithFrame:CGRectMake(leftOrigin, topOrigin, widgetWidth, widgetHeight)];
    //         [widget addItemsWithTitles:[CPArray arrayWithArray:obj.choices]];
    //     }

    //     [self addSubview:widget];
    //     [label setObjectValue:labelString];
    //     [self addSubview:label];

    //     prevWidget = widget;
    //     topOrigin += widgetHeight + 5;  // add 5 pixels spacing between fields

    //     viewHeight += 30;
    // }
}

- (id)drawRect:(CGRect)aRect
{
    console.log("Draw rect called!");
    [[CPColor yellowColor] set];
    var ctx = [[CPGraphicsContext currentContext] graphicsPort];
    CGContextFillRect(ctx, aRect);
}

- (@action)removeSelfFromWorkflow:(id)aSender
{
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanRemoveJobFromWorkflowNotification
                                      object:self];

}

@end
