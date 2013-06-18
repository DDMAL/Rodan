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
            CPPredicate         _categoryPredicate;
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
        [self _populateCategoryMenu];
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
    // Add 'All' menu item.
    var menuItemCategory = [[CPMenuItem alloc] initWithTitle:"All"
                                               action:null
                                               keyEquivalent:null];
    [_menuCategory addItem:menuItemCategory];

    // Next, enumerate through our jobs and get distinct category names.
    var jobArrayEnumerator = [[jobArrayController content] objectEnumerator],
        job = null;
    while (job = [jobArrayEnumerator nextObject])
    {
        if ([_menuCategory itemWithTitle:[job category]] === null)
        {
            var menuItemCategory = [[CPMenuItem alloc] initWithTitle:[job category]
                                                       action:null
                                                       keyEquivalent:null];
            [_menuCategory addItem:menuItemCategory];
        }
    }

    // Enable 'em.
    [_menuCategory setAutoenablesItems:YES];
}

- (void)_populateIsInteractiveMenu
{
    if (_menuIsInteractive !== null)
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
        [_menuIsInteractive addItem:_menuItemIsInteractiveAll];
        [_menuIsInteractive addItem:_menuItemIsInteractiveInteractive];
        [_menuIsInteractive addItem:_menuItemIsInteractiveNonInteractive];
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
    var highlightedItem = [aMenu highlightedItem];
    if ([highlightedItem title] !== "All")
    {
        _categoryPredicate = [CPPredicate predicateWithFormat:"category like '" + [highlightedItem title] + "'"];
    }
    else
    {
        _categoryPredicate = null;
    }
    [self _applyPredicates];
}

- (void)_applyPredicates
{
    var predicateArray = [[CPArray alloc] initWithObjects:_isInteractivePredicate, _categoryPredicate];
    if (_isInteractivePredicate !== null)
    {
        predicateArray.push(_isInteractivePredicate);
    }
    if (_categoryPredicate !== null)
    {
        predicateArray.push(_categoryPredicate);
    }
    var masterPredicate = [CPCompoundPredicate andPredicateWithSubpredicates:predicateArray];
    [jobArrayController setFilterPredicate:masterPredicate];
}
@end
