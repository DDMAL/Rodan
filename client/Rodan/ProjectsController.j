@import <Foundation/CPObject.j>
@import "RodanAPIController.j"

var COLUMN_ID = @"ProjectName";

@implementation ProjectsController : CPObject
{
    CPOutlineView   outlineView     @accessors;
    CPTableColumn   tableColumn     @accessors;
    CPMutableArray  projectResults  @accessors;
    CPScrollView    parentScrollView @accessors;
    CPDictionary    items;
}

- (id)init
{
    self = [super init];
    if (self)
    {
        [[CPNotificationCenter defaultCenter] addObserver:self
                                                 selector:@selector(resultCallback:)
                                                 name:@"ProjectsFetchedNotification"
                                                 object:nil];

        [RodanAPIController initWithRequest:"project" notification:@"ProjectsFetchedNotification"];
        projectResults = [[CPMutableArray alloc] init];
    }
    return self;
}

+ (id)initWithOutlineView:(CPScrollView)parentScrollView
{
    var thisOutlineView = [[self alloc] init];

    [thisOutlineView setParentScrollView:parentScrollView];

    return thisOutlineView;
}

- (void)resultCallback:(CPNotification)aNotification
{
    CPLog("Result Callback for Project View Controller");
    [projectResults setArray:[aNotification object]];

    var projectsHeader = @"MY PROJECTS",
        groupsHeader = @"GROUP PROJECTS";

    items = [CPDictionary dictionaryWithObjects:[[@"Awesome Project", @"Great Project"], [@"Group Project 1", @"Group Project 2"]] forKeys:[projectsHeader, groupsHeader]];

    outlineView = [[CPOutlineView alloc] initWithFrame:[parentScrollView bounds]];
    [outlineView setBackgroundColor:[CPColor clearColor]];
    [outlineView setAction:@selector(outlineViewAction:)];
    // [outlineView setTarget:self];
    [outlineView setDataSource:self];
    [outlineView setDelegate:self];
    [outlineView setAllowsMultipleSelection:NO];
    [outlineView setHeaderView:nil];
    [outlineView setCornerView:nil];
    [outlineView setUsesAlternatingRowBackgroundColors:NO];
    [outlineView setAutoresizingMask:CPViewWidthSizable];

    tableColumn = [[CPTableColumn alloc] initWithIdentifier:COLUMN_ID];
    [tableColumn setWidth:CGRectGetWidth([parentScrollView bounds])];
    // [tableColumn setDataView:[[CPView alloc] init]];

    [outlineView addTableColumn:tableColumn];
    [outlineView setOutlineTableColumn:tableColumn];

    // [outlineView reloadData];
}

- (void)outlineViewAction
{
    CPLog("Outline View Action method");
}

- (id)outlineView:(CPOutlineView)theOutlineView child:(CPInteger)index ofItem:(id)item
{
    CPLog("outlineView:child:ofItem");
    if (item === nil)
    {
        var keys = [items allKeys];
        return [keys objectAtIndex:index];
    }
    else
    {
        var values = [items objectForKey:item];
        return [values objectAtIndex:index];
    }

}

- (BOOL)outlineView:(CPOutlineView)theOutlineView isItemExpandable:(id)item
{
    CPLog("outlineView:isItemExpandable");
    var values = [items objectForKey:item];
    return ([values count] > 0);
}

- (CPInteger)outlineView:(CPOutlineView)theOutlineView numberOfChildrenOfItem:(id)item
{
    CPLog("outlineView:numberOfChildrenOfItem");
    CPLog([items count]);
    if (item === nil)
    {
        return [items count];
    }
    else
    {
        var values = [items objectForKey:item];
        return [values count];
    }
}

- (id)outlineView:(CPOutlineView)outlineView objectValueForTableColumn:(CPTableColumn)tableColumn byItem:(id)item
{
    CPLog("outlineView:objectValueForTableColumn:byItem");
    CPLog(item);
    return item;
}

@end


/* Simple node object for tree objects */
@implementation Node : CPObject
{
    CPString        name     @accessors;
    CPString        path     @accessors;
    CPImage         image    @accessors;
    CPMutableArray  children @accessors;
}

- (id)init
{
    self = [super init];
    if (self)
    {
        name = @"Untitled";
    }
    return self;
}

- (id)initWithName:(CPString)aName
{
    self = [super init];
    if (self)
    {
        name = aName;
    }
    return self;
}



@end
