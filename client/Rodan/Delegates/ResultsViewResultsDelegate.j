@import <Foundation/CPObject.j>
@import "../Models/SimpleResult.j"


/**
 * Delegate to handle the results table in the Results view.
 */
@implementation ResultsViewResultsDelegate : CPObject
{
    @outlet CPArrayController   _resultArrayController;
            SimpleResult        _currentlySelectedResult;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)setArrayContents:(CPArray)aContents
{
    [_resultArrayController setContent:aContents];
    if ([[_resultArrayController content] count] == 0)
    {
        _currentlySelectedResult = nil;
    }
}

/**
 * Initializes packaging of results.
 */
- (void)returnResults:(CPString)aResult
{
    window.open(aResult, "_blank");
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedResult = nil;
}

- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedResult = [[_resultArrayController contentArray] objectAtIndex:rowIndex];
    return YES;
}
@end
