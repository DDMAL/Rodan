@import "../Models/Job.j"

@global RodanDidLoadJobsNotification
@global RodanJobTreeNeedsRefresh

@implementation JobController : CPObject
{
    @outlet CPOutlineView       categoryOutlineView;
    @outlet CPTableView         serverAdminJobsList;

    @outlet CPArrayController   jobArrayController;
            JobOutlineViewDelegate  outlineViewDelegate;
}

- (id)init
{
    if (self = [super init])
    {
    }
    return self;
}

- (void)fetchJobs
{

    [WLRemoteAction schedule:WLRemoteActionGetType path:"/jobs?is_enabled=1" delegate:self message:"Loading jobs"];
}

- (void)remoteActionDidFinish:(WLRemoteAction)anAction
{
    CPLog("Remote Job Action did Finish");
    if ([anAction result])
    {
        var j = [Job objectsFromJson:[anAction result]];
        [jobArrayController addObjects:j];

        // boot up the delegate for the outline view
        [JobOutlineViewDelegate withOutlineView:categoryOutlineView];

        [[CPNotificationCenter defaultCenter] postNotificationName:RodanDidLoadJobsNotification
                                              object:[anAction result]];
    }
}

@end


/*
    This handles most of the work for the job outline view in the 'create workflow' window.
    It will probably need to be refactored sometime soon, but for now it works.
*/
@implementation JobOutlineViewDelegate : CPObject
{
    CPTreeNode      rootTreeNode    @accessors;
    CPOutlineView   theOutlineView  @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        var center = [CPNotificationCenter defaultCenter];
        [center addObserver:self selector:@selector(didLoadJobs:) name:RodanDidLoadJobsNotification object:nil];
        [center addObserver:self selector:@selector(refreshOutlineView:) name:RodanJobTreeNeedsRefresh object:nil];

        [theOutlineView registerForDraggedTypes:["TestData"]];
    }
    return self;
}

+ (void)withOutlineView:(CPOutlineView)anOutlineView
{
    var theDelegate = [[JobOutlineViewDelegate alloc] init];
    [anOutlineView setDataSource:theDelegate];
    [theDelegate setTheOutlineView:anOutlineView];
}

- (CPArray)childrenForItem:(id)anItem
{
    if (anItem == nil)
        return [rootTreeNode childNodes];
    else
        return [anItem childNodes];
}

- (void)didLoadJobs:(id)aNotification
{
    var results = [[CPArray alloc] initWithArray:[aNotification object]],
        jobsByCategory = [[CPMutableDictionary alloc] init],
        treeStructure = [[CPMutableArray alloc] init];

    /*
        Loop through the results and organize the returned jobs into
        jobs according to their category.
    */
    [results enumerateObjectsUsingBlock:function(object, idx, stop)
    {
        if (![jobsByCategory containsKey:object.category])
        {
            [jobsByCategory setValue:[[CPMutableArray alloc] init] forKey:object.category];
        }
        var childNode = [CPTreeNode treeNodeWithRepresentedObject:[[TreeNode alloc] initWithName:object.name]];
        [[jobsByCategory valueForKey:object.category] addObject:childNode];
    }];

    /*
        Create the tree structure that we'll be sending to our outline view
    */
    [jobsByCategory enumerateKeysAndObjectsUsingBlock:function(key, value, stop)
    {
        var nodeObject = [[TreeNode alloc] initWithName:key],
            treeNode = [CPTreeNode treeNodeWithRepresentedObject:nodeObject];
        [[treeNode mutableChildNodes] addObjectsFromArray:value];
        [treeStructure addObject:treeNode];
    }];

    rootTreeNode = [CPTreeNode treeNodeWithRepresentedObject:[[TreeNode alloc] initWithName:nil]];
    [[rootTreeNode mutableChildNodes] addObjectsFromArray:treeStructure];


    [[CPNotificationCenter defaultCenter] postNotificationName:RodanJobTreeNeedsRefresh
                                          object:nil];
}

#pragma mark -
#pragma mark CPOutlineView delegate methods

- (id)outlineView:(CPOutlineView)outlineView child:(CPInteger)anIndex ofItem:(id)anItem
{
    return [[self childrenForItem:anItem] objectAtIndex:anIndex];
}

- (BOOL)outlineView:(CPOutlineView)outlineView isItemExpandable:(id)anItem
{
    return [[self childrenForItem:anItem] count] > 0;
}

- (int)outlineView:(CPOutlineView)outlineView numberOfChildrenOfItem:(id)anItem
{
    return [[self childrenForItem:anItem] count];
}

- (id)outlineView:(CPOutlineView)outlineView objectValueForTableColumn:(CPTableColumn)tableColumn byItem:(id)anItem
{
    return [[anItem representedObject] humanName];
}

- (CPDragOperation)outlineView:(CPOutlineView)anOutlineView
                   validateDrop:(id < CPDraggingInfo >)theInfo
                   proposedItem:(id)theItem
                   proposedChildIndex:(int)theIndex
{
    console.log("Drag!");
    return CPDragOperationEvery;
}

- (BOOL)outlineView:(CPOutlineView)anOutlineView writeItems:(CPArray)theItems toPasteboard:(CPPasteBoard)thePasteBoard
{
    [thePasteBoard declareTypes:["TestData"] owner:self];
    [thePasteBoard setData:[CPKeyedArchiver archivedDataWithRootObject:theItems] forType:"testData"];

    return YES;
}

- (BOOL)outlineView:(CPOutlineView)outlineView acceptDrop:(id < CPDraggingInfo >)theInfo item:(id)theItem childIndex:(int)theIndex
{
    console.log("Can Drop?");
    return NO;
}

#pragma mark -

- (void)refreshOutlineView:(id)aNotification
{
    [theOutlineView reloadData];
}

@end


/* A node object for the outline view */
@implementation TreeNode : CPObject
{
    CPString    name   @accessors;
}

- (id)init
{
    if (self = [super init])
    {
        name = @"New Node";
    }
    return self;
}

- (id)initWithName:(CPString)aName
{
    var self = [self init];
    name = aName;
    return self;
}

+ (TreeNode)nodeDataWithName:(CPString)aName
{
    return [[TreeNode alloc] initWithName:aName];
}

- (CPString)humanName
{
    var splitString = [name componentsSeparatedByString:"."];
    if ([splitString count] > 1)
    {
        var theName = [[splitString lastObject] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        return [theName capitalizedString];
    }
    return name;
}
@end
