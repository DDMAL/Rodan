@global RodanShouldLoadWorkflowDesignerNotification

JobItemType = @"JobItemType";
activeWorkflow = nil;

@implementation WorkflowDesignerController : CPObject
{
    @outlet     CPArrayController       workflowArrayController;
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

    [jobList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
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

@end

@implementation WorkflowDesignerDelegate : CPObject
{
    @outlet     CPTableView     currentWorkflow;
}

- (void)tableView:(CPTableView)aTableView dataViewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    console.log("data view for table column");
    var aView = [currentWorkflow makeViewWithIdentifier:[aTableColumn identifier] owner:self];
    return aView;
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

- (BOOL)tableView:(CPTableView)aTableView acceptDrop:(id)info row:(int)row dropOperation:(CPTableViewDropOperation)operation
{
    console.log("accept drop?");
    return YES;
}

@end

@implementation JobListDelegate : CPObject
{
}

- (BOOL)tableView:(CPTableView)aTableView writeRowsWithIndexes:(CPIndexSet)rowIndexes toPasteboard:(CPPasteboard)pboard
{
    console.log("write rows with indexes");
    [pboard declareTypes:[CPArray arrayWithObject:JobItemType] owner:self];
    [pboard setData:rowIndexes forType:JobItemType];

    return YES;
}

@end
