@import <LPKit/LPMultiLineTextField.j>
@import "../Models/Job.j"

@global activeUser
@global RodanShouldLoadWorkflowDesignerNotification
@global RodanDidLoadWorkflowNotification
@global RodanRemoveJobFromWorkflowNotification
@global JOBSETTING_TYPE_UUIDWORKFLOWJOB

JobItemType = @"JobItemType";

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
    [self _removeWorkflowJobs:deletedObjects
          fromWorkflowJobSettings:[currentWorkflowArrayController content]];
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

/*
    Validates the drag-and-drop of Jobs into the Workflow. When a Job is dragged into the workflow,
    this method will check if the input and output types of the jobs match with the surrounding jobs.
    If everything checks out it will create a new WorkflowJob resource from the Job object, and allow
    the drop; otherwise it will not.
*/
- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)anIndex dropOperation:(CPTableViewDropOperation)aDropOperation
{
    var content = [jobArrayController arrangedObjects],
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

        if (anIndex === 0)
        {
            nextObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex];
            inputTypePasses = YES;
            outputTypePasses = [self _checkOutputTypeMatches:nextObject withPixelTypes:outputPixelTypes];
        }
        else if (anIndex === contentArrayCount)
        {
            prevObject = [[currentWorkflowArrayController contentArray] objectAtIndex:anIndex - 1];
            inputTypePasses = [self _checkInputTypeMatches:prevObject withPixelTypes:inputPixelTypes];
            outputTypePasses = YES;
        }
        else
        {
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
            "workflow": [[WorkflowController activeWorkflow] pk],
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

- (void)_removeWorkflowJobs:(CPArray)aDeletedWorkflowJobs
        fromWorkflowJobSettings:(CPArray)aWorkflowJobs
{
    var adjusted = NO;
    if (aDeletedWorkflowJobs != nil && aWorkflowJobs != nil)
    {
        // Get the PKs.
        var deletedWorkflowJobPkArray = [[CPMutableArray alloc] init],
            deletedWorkflowJobEnumerator = [aDeletedWorkflowJobs objectEnumerator],
            deletedWorkflowJob = nil;
        while (deletedWorkflowJob = [deletedWorkflowJobEnumerator nextObject])
        {
            [deletedWorkflowJobPkArray addObject:[deletedWorkflowJob pk]];
        }

        // Go through the remaining workflow jobs.
        var workflowJobEnumerator = [aWorkflowJobs objectEnumerator],
            workflowJob = nil;
        while (workflowJob = [workflowJobEnumerator nextObject])
        {
            // Go through the job settings for the workflow.
            var jobSettingsEnumerator = [[workflowJob jobSettings] objectEnumerator],
                jobSetting = nil;
            while (jobSetting = [jobSettingsEnumerator nextObject])
            {
                if ([jobSetting settingType] == JOBSETTING_TYPE_UUIDWORKFLOWJOB)
                {
                    // If this workflow job references one of the deleted jobs, we have to remove it.
                    var index = [deletedWorkflowJobPkArray indexOfObject:[jobSetting settingDefault]];
                    if (index >= 0)
                    {
                        [jobSetting setSettingDefault:nil];
                        adjusted = YES;
                    }
                }
            }
        }
    }

    // Do a save if there was an adjustment.
    var workflow = [WorkflowController activeWorkflow];
    if (workflow != nil && adjusted)
    {
        [workflow touchWorkflowJobs];
    }
}
@end
