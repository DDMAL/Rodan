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
}


////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)setArrayContents:(CPArray)aContents
{
    [_pageArrayController setContent:aContents];
    if ([[_pageArrayController content] count] == 0)
    {
        _currentlySelectedPage = nil;
        [_resultsViewResultsDelegate setArrayContents:nil];
    }
}


////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)tableViewSelectionIsChanging:(CPNotification)aNotification
{
    _currentlySelectedPage = nil;
    [_resultsViewResultsDelegate setArrayContents:nil];
}


- (BOOL)tableView:(CPTableView)aTableView shouldSelectRow:(int)rowIndex
{
    _currentlySelectedPage = [[_pageArrayController contentArray] objectAtIndex:rowIndex];
    [_resultsViewResultsDelegate setArrayContents:[_currentlySelectedPage results]];
    return YES;
}
@end
