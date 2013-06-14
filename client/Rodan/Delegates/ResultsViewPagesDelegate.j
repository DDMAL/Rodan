@import <Foundation/CPObject.j>
@import "../Delegates/ResultsViewResultsDelegate.j"
@import "../Models/SimplePage.j"


/**
 * Delegate to handle the pages table in the Results view.
 */
@implementation ResultsViewPagesDelegate : CPObject
{
    @outlet ResultsViewResultsDelegate  _resultsViewResultsDelegate;
    @outlet CPArrayController           _pageArrayController;
            SimplePage                  _currentlySelectedPage;
            int                         _currentlySelectedRowIndex;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)setArrayContents:(CPArray)aContents
{
    [_pageArrayController setContent:aContents];
    if ([[_pageArrayController content] count] == 0)
    {
        _currentlySelectedRowIndex = -1;
        [_resultsViewResultsDelegate setArrayContents:nil];
    }
    [self _repointCurrentlySelectedObject];

    // If something is currently selected, we should updated results.
    if (_currentlySelectedRowIndex >= 0)
    {
        [_resultsViewResultsDelegate setArrayContents:[_currentlySelectedPage results]];
    }
}


- (id)init
{
    _currentlySelectedRowIndex = -1;
    return self;
}


////////////////////////////////////////////////////////////////////////////////////////////
// Private Methods
////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Repoints the currently selected object.
 */
- (void)_repointCurrentlySelectedObject
{
    if (_currentlySelectedRowIndex >= 0)
    {
        _currentlySelectedPage = [[_pageArrayController contentArray] objectAtIndex:_currentlySelectedRowIndex];
    }
    else
    {
        _currentlySelectedPage = nil;
    }
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    // Update ourselves.
    _currentlySelectedRowIndex = -1;
    [self _repointCurrentlySelectedObject];

    // Inform others.
    [_resultsViewResultsDelegate setArrayContents:nil];
}


- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedRowIndex = rowIndex;
    [self _repointCurrentlySelectedObject];
    [_resultsViewResultsDelegate setArrayContents:[_currentlySelectedPage results]];
    return YES;
}
@end
