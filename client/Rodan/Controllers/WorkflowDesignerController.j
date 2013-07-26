@import <LPKit/LPMultiLineTextField.j>

@import "../Delegates/LoadActiveWorkflowDelegate.j"
@import "../Delegates/WorkflowDesignerDelegate.j"
@import "../Models/Page.j"
@import "../Models/WorkflowJobSetting.j"

@global activeUser
@global RodanHasFocusWorkflowDesignerViewNotification
@global RodanShouldLoadWorkflowDesignerNotification
@global RodanShouldLoadClassifiersNotification
@global RodanShouldLoadPagesNotification
@global RodanDidLoadWorkflowNotification
@global RodanRemoveJobFromWorkflowNotification
@global RodanShouldLoadWorkflowDesignerDataNotification
@global RodanShouldLoadWorkflowsNotification

JobItemType = @"JobItemType";

var _msLOADINTERVAL = 5.0;

@implementation WorkflowDesignerController : CPObject
{
    @outlet     CPObject                menuItemsController;
    @outlet     CPArrayController       workflowArrayController;

    @outlet     CPTableView             currentWorkflow;
    @outlet     CPArrayController       currentWorkflowArrayController;
    @outlet     CPArrayController       workflowPagesArrayController;

    @outlet     CPWindow                addPagesToWorkflowWindow;
    @outlet     CPButton                addPagesToWorkflowButton;
    @outlet     CPTableView             addPagesToWorkflowTableView;

    @outlet     LoadActiveWorkflowDelegate loadActiveWorkflowDelegate;

    @outlet     CPTableView             jobList;

    @outlet     TNTabView               pageRunTabView;

    @outlet     CPView                  pageTab;
    @outlet     CPTableView             pageList;
    @outlet     CPArrayController       pageArrayController;
    @outlet     CPView                  pageThumbnailView;
    @outlet     CPButtonBar             pageListAddRemoveButtonBar;

    @outlet     CPView                  runTab;
    @outlet     CPTableView             runList;
    @outlet     CPArrayController       runArrayController;
    @outlet     CPButtonBar             runAddRemoveButtonBar;

    @outlet     TNTabView               workflowJobTabView;
    @outlet     CPView                  selectedWorkflowJobSettingsTab;
    @outlet     CPView                  selectedWorkflowJobDescriptionTab;
    @outlet     LPMultiLineTextField    selectedWorkflowJobDescription;
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

    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(setWorkflowMenu:)
                                          name:RodanDidLoadWorkflowNotification
                                          object:nil];

    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(receiveHasFocusEvent:)
                                          name:RodanHasFocusWorkflowDesignerViewNotification
                                          object:nil];

    [[CPNotificationCenter defaultCenter] addObserver:self
                                          selector:@selector(handleShouldLoadWorkflowDesignerData:)
                                          name:RodanShouldLoadWorkflowDesignerDataNotification
                                          object:nil];

    [jobList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [pageList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [runList setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    // [currentWorkflow setBackgroundColor:[CPColor colorWithHexString:@"DEE3E9"]];
    [currentWorkflow setGridStyleMask:CPTableViewSolidHorizontalGridLineMask];
    [currentWorkflow registerForDraggedTypes:[JobItemType]];

    // page and run tab view
    var tab1 = [[CPTabViewItem alloc] initWithIdentifier:@"pageListTab"],
        tab2 = [[CPTabViewItem alloc] initWithIdentifier:@"runListTab"];
    [tab1 setLabel:@"Pages"];
    [tab1 setView:pageTab];

    [tab2 setLabel:@"Runs"];
    [tab2 setView:runTab];

    [pageRunTabView addTabViewItem:tab1];
    [pageRunTabView addTabViewItem:tab2];

    var addButton = [CPButtonBar plusPopupButton],
        removeButton = [CPButtonBar minusButton],
        addPagesTitle = @"Add Pages to Workflow...";
    [addButton addItemsWithTitles:[addPagesTitle]];

    var addPagesItem = [addButton itemWithTitle:addPagesTitle];
    [pageListAddRemoveButtonBar setButtons:[addButton, removeButton]];

    [addPagesItem setAction:@selector(openAddPagesWindow:)];
    [addPagesItem setTarget:self];

    [removeButton setAction:@selector(removePagesFromWorkflow:)];
    [removeButton setTarget:self];

    [removeButton bind:@"enabled"
                  toObject:workflowPagesArrayController
                  withKeyPath:@"selection.pk"
                  options:nil];

    // [removeButton bind:@""]

    // Inspector Pane
    var tab1 = [[CPTabViewItem alloc] initWithIdentifier:@"settingsTab"],
        tab2 = [[CPTabViewItem alloc] initWithIdentifier:@"descriptionTab"];
    [tab1 setLabel:@"Settings"];
    [tab1 setView:selectedWorkflowJobSettingsTab];
    [tab2 setLabel:@"Description"];
    [tab2 setView:selectedWorkflowJobDescriptionTab];
    [workflowJobTabView addTabViewItem:tab1];
    [workflowJobTabView addTabViewItem:tab2];

    [selectedWorkflowJobDescription bind:@"value"
                                    toObject:currentWorkflowArrayController
                                    withKeyPath:@"selection.jobDescription"
                                    options:nil];
}

- (void)receiveHasFocusEvent:(CPNotification)aNotification
{
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowsNotification
                                          object:nil];
    [RKNotificationTimer setTimedNotification:_msLOADINTERVAL
                         notification:RodanShouldLoadWorkflowDesignerDataNotification];
}

- (void)setWorkflowMenu:(CPNotification)aNotification
{
    [menuItemsController setDesignerIsActive:YES];
}

- (void)shouldLoadWorkflow:(CPNotification)aNotification
{
    [WLRemoteAction schedule:WLRemoteActionGetType
                    path:[[aNotification object] pk]
                    delegate:loadActiveWorkflowDelegate
                    message:"Loading Workflow Jobs"];
}

/**
 * Start notification cycle.
 */
- (void)handleShouldLoadWorkflowDesignerData:(CPNotification)aNotification
{
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadClassifiersNotification
                                          object:nil];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadPagesNotification
                                          object:nil];
}

- (@action)selectWorkflow:(id)aSender
{
    var selectedWorkflow = [[workflowArrayController selectedObjects] objectAtIndex:0];
    [WorkflowController setActiveWorkflow:selectedWorkflow];
    [[CPNotificationCenter defaultCenter] postNotificationName:RodanShouldLoadWorkflowDesignerNotification
                                          object:selectedWorkflow];
}

- (@action)removeJobFromWorkflow:(CPNotification)aSender
{
    [currentWorkflowArrayController removeObject:[[aSender object] objectValue]];
    [[[aSender object] objectValue] ensureDeleted];
}

- (@action)removePagesFromWorkflow:(id)aSender
{
    //pass
}

- (@action)openAddPagesWindow:(id)aSender
{
    // [addImagesToWorkflowWindow makeKeyAndOrderFront:aSender];
    [addPagesToWorkflowWindow setDefaultButton:addPagesToWorkflowButton];
    [CPApp beginSheet:addPagesToWorkflowWindow
           modalForWindow:[CPApp mainWindow]
           modalDelegate:self
           didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (@action)closeAddPagesSheet:(id)aSender
{
    if ([aSender tag] === 0)
    {
        var myObjects = [pageArrayController selectedObjects];
        [workflowPagesArrayController addObjects:myObjects];
    }

    [CPApp endSheet:addPagesToWorkflowWindow returnCode:[aSender tag]];
}

- (void)didEndSheet:(CPWindow)aSheet returnCode:(int)returnCode contextInfo:(id)contextInfo
{
    [addPagesToWorkflowWindow orderOut:self];
}
@end

/***
    A simple class that handles some of the delegate methods to support drag-n-drop.
***/
@implementation JobListDelegate : CPObject
{
}

- (int)numberOfRowsInTableView:(CPTableView)aTableView
{
    // needed so that it doesn't complain about not having the delegate function.
}

- (BOOL)tableView:(CPTableView)aTableView writeRowsWithIndexes:(CPIndexSet)rowIndexes toPasteboard:(CPPasteboard)pboard
{
    [pboard declareTypes:[JobItemType] owner:self];
    [pboard setData:rowIndexes forType:JobItemType];

    return YES;
}
@end

@implementation PageListDelegate : CPObject
{
    @outlet     CPArrayController       pageArrayController;
}

- (void)tableView:(CPTableView)aTableView viewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
{
    var aView = [aTableView makeViewWithIdentifier:@"workflowPage" owner:self];

    return aView;
}
@end

@implementation PageListCellView : CPView
{
    id          objectValue @accessors;
    CPTextField textField   @accessors;
}

- (id)init
{
    self = [super init];
    return self;
}

- (id)initWithFrame:(CGRect)aFrame
{
    self = [super initWithFrame:aFrame];
    return self;
}

- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder];
    return self;
}

- (void)setObjectValue:(id)aValue
{
    objectValue = aValue;
}
@end

