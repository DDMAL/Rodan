@import "../Models/Job.j"
@import "../Models/TreeNode.j"

@global RodanDidLoadJobsNotification
@global RodanJobTreeNeedsRefresh

@implementation JobController : CPObject
{
    @outlet CPArrayController   jobArrayController;
    @outlet CPMenu              _menuIsInteractive;
    @outlet CPMenu              _menuCategory;
            CPMenuItem          _menuItemIsInteractiveAll;
            CPMenuItem          _menuItemIsInteractiveInteractive;
            CPMenuItem          _menuItemIsInteractiveNonInteractive;
            CPPredicate         _masterPredicate;
            CPPredicate         _isInteractivePredicate;
}

////////////////////////////////////////////////////////////////////////////////////////////
// Init Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (void)awakeFromCib
{
    [self _populateIsInteractiveMenu];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)fetchJobs
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:"/jobs/?enabled=1"
                    delegate:self
                    message:"Loading jobs"];
}

////////////////////////////////////////////////////////////////////////////////////////////
// Handler Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    if ([anAction result])
    {
        var j = [Job objectsFromJson:[anAction result]];
        [jobArrayController addObjects:j];
        [self _applyPredicates];
        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadJobsNotification
                                              object:[anAction result]];
    }
}

- (void)menuDidClose:(CPMenu)aMenu
{
    switch (aMenu)
    {
        case _menuCategory:
        {
            [self _handleCategoryMenuDidClose:aMenu];
            break;
        }

        case _menuIsInteractive:
        {
            [self _handleIsInteractiveMenuDidClose:aMenu];
            break;
        }

        default:
        {
            break;
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////
// Private Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (void)_populateCategoryMenu
{

}

- (void)_populateIsInteractiveMenu
{
    if (_menuIsInteractive != null)
    {
        // Create items.
        _menuItemIsInteractiveAll = [[CPMenuItem alloc] initWithTitle:"All"
                                                        action:null
                                                        keyEquivalent:null];
        _menuItemIsInteractiveInteractive = [[CPMenuItem alloc] initWithTitle:"Interactive"
                                                                 action:null
                                                                 keyEquivalent:null];
        _menuItemIsInteractiveNonInteractive = [[CPMenuItem alloc] initWithTitle:"Non-interactive"
                                                                   action:null
                                                                   keyEquivalent:null];

        // Add to menu.
        [_menuIsInteractive insertItem:_menuItemIsInteractiveAll atIndex:0];
        [_menuIsInteractive insertItem:_menuItemIsInteractiveInteractive atIndex:1];
        [_menuIsInteractive insertItem:_menuItemIsInteractiveNonInteractive atIndex:2];
        [_menuIsInteractive setAutoenablesItems:YES];
    }
}

- (void)_handleIsInteractiveMenuDidClose:(CPMenu)aMenu
{
    switch ([aMenu highlightedItem])
    {
        case _menuItemIsInteractiveAll:
        {
            _isInteractivePredicate = null;
            break;
        }

        case _menuItemIsInteractiveInteractive:
        {
            _isInteractivePredicate = [CPPredicate predicateWithFormat:"isInteractive == true"];
            break;
        }

        case _menuItemIsInteractiveNonInteractive:
        {
            _isInteractivePredicate = [CPPredicate predicateWithFormat:"isInteractive == false"];
            break;
        }

        default:
        {
            _isInteractivePredicate = null;
            break;
        }
    }
    [self _applyPredicates];
}

- (void)_handleCategoryMenuDidClose:(CPMenu)aMenu
{

}

- (void)_applyPredicates
{
    var predicateArray = [[CPArray alloc] initWithObjects:_isInteractivePredicate],
        masterPredicate = [CPCompoundPredicate andPredicateWithSubpredicates:predicateArray];
    [jobArrayController setFilterPredicate:masterPredicate];
}
@end
