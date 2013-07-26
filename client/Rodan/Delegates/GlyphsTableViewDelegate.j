@import "../Views/PhotoView.j"
@import "../Views/ViewWithObjectValue.j"
@import "../Models/SymbolCollection.j"
@import "../Models/GameraGlyphs.j"

@implementation GlyphsTableViewDelegate : CPObject
{
    // @outlet CPArrayController       symbolCollectionArrayController;
            int                     headerLabelHeight   @accessors;
    @outlet CPTableView             theTableView;
    @outlet GlyphsTableViewDelegate theOtherTableViewDelegate;
            GameraGlyphs            theGameraGlyphs     @accessors;
}

- (void)init
{
    if (self = [super init])
    {
        [self setHeaderLabelHeight:20];
        // [[CPNotificationCenter defaultCenter] addObserver:self selector:@selector(scrollViewContentBoundsDidChange:) name:CPViewBoundsDidChangeNotification object:self.scrollView.contentView];
            // This is if I want to try to write the tableview to not do a complete and utter reload every time something changes, and instead to just reload the current view.
    }

    return self;
}

- (void)initializeTableView
{
    // Deprecated.
    [theTableView reloadData];
}

- (void)reloadData
{
    [theTableView reloadData];
}

- (CPMutableArray)writeSymbolName:(CPString)newName
{
    var symbolCollections = [theGameraGlyphs symbolCollections],
        symbolCollectionsCount = [symbolCollections count],
        allWrittenGlyphs = [[CPMutableArray alloc] init];

    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        var cvArrayController = [symbolCollections[i] cvArrayController],
            selectedObjects = [cvArrayController selectedObjects];

        [allWrittenGlyphs addObjectsFromArray:selectedObjects];
    }

    var emptyIndexSet = [CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)];

    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        [[symbolCollections[i] cvArrayController] setSelectionIndexes:emptyIndexSet];
    }

    console.log("GlyphsTableView starting to change glyphs (" + [self class] + ".)");
    [allWrittenGlyphs makeObjectsPerformSelector:@"makeDirtyProperty:" withObject:@"classifierPk"];
    [allWrittenGlyphs makeObjectsPerformSelector:@"makeDirtyProperty:" withObject:@"pageGlyphsPk"];
    [allWrittenGlyphs makeObjectsPerformSelector:@"writeSymbolName:" withObject:newName];
    [allWrittenGlyphs makeObjectsPerformSelector:@"ensureSaved"];
    console.log("GlyphsTableView ensureSaved done on all glyphs (" + [self class] + ".)");

    [theTableView reloadData];

    return allWrittenGlyphs;
}

- (void)close
{
    [[theGameraGlyphs symbolCollectionsArrayController] setContent:[]];
    [theTableView noteNumberOfRowsChanged];  // Seems unnecessary
    [theTableView reloadData];
}

// ------------------------------------- DELEGATE METHODS ----------------------------------------------

- (CPView)tableView:(CPTableView)aTableView viewForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
// Return a view for the TableView to use a cell of the table.
{
    // console.log('---viewForTableColumn---');
    // if (cachedViews[aRow])
    // {
    //     return cachedViews[aRow];
    // }
    // else
    // {
    //     cachedViews[aRow] = [[ViewWithObjectValue alloc] initWithFrame:CGRectMakeZero()];
    //     return cachedViews[aRow];  // Nope... doesn't display!
    // }
    // console.log([cvArrayControllers[0] selectionIndexes]);
    return [[ViewWithObjectValue alloc] initWithFrame:CGRectMakeZero()];
}

- (void)tableView:(CPTableView)aTableView willDisplayView:(CPView)aView forTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
// Set up the view to display.  (Delegate method.)
// (Note: I do things in this function so that I have access to objectValue... which I don't in viewForTableColumn.)
{
    console.log("---willDisplayView--- row " + aRow);
    var symbolCollection = [[aTableView dataSource] tableView:aTableView objectValueForTableColumn:aTableColumn row:aRow],
        cvArrayController = [symbolCollection cvArrayController],
        symbolName = [symbolCollection symbolName],  // If I use binding for the label stringValue, I don't need this variable
        label = [[CPTextField alloc] initWithFrame:CGRectMake(0,0,CGRectGetWidth([aView bounds]), [self headerLabelHeight])];
    [label setStringValue:symbolName];
    [label setFont:[CPFont boldSystemFontOfSize:16]];
    [label setAutoresizesSubviews:NO];
    [label setAutoresizingMask:CPViewWidthSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMinYMargin];
    [aView addSubview:label];

    var parentView = [[CPView alloc] initWithFrame:CGRectMakeZero()];
    [aView setAutoresizesSubviews:NO];
        //It's driving me bonkers: why doesn't the label get pinned to the top of aView upon resize???  (Not using Autosize!)
    [aView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMinYMargin | CPViewMaxYMargin];
    [parentView setAutoresizesSubviews:NO];
    [parentView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMaxYMargin];  // Shouldn't be Y sizable since I'm forcing the collection view into a small space

    [aView addSubview:parentView];
    [parentView setFrame:CGRectMake(0, [self headerLabelHeight], CGRectGetWidth([aView bounds]), CGRectGetHeight([aView bounds]) - [self headerLabelHeight])];

    var cv = [self _makeCollectionViewForTableView:aTableView arrayController:cvArrayController parentView:parentView row:aRow];
    // [cv bind:@"selectionIndexes" toObject:cvArrayControllers[aRow] withKeyPath:@"selectionIndexes" options:nil];
    [cv setSelectionIndexes:[cvArrayController selectionIndexes]];  // This should allow you to scroll down and back and have the selection persist
        // Now... when did cvArrayControllers[aRow] selectionIndexes get erased!
        // Maybe the binding isn't working... or maybe the array controller
    [cvArrayController bind:@"selectionIndexes" toObject:cv withKeyPath:@"selectionIndexes" options:nil];
        // Note: this is a clever binding.  We don't want to bind the view to the array controller because the view is transitory
        // and we'd end up with an accumulation of bindings.
        // Gweh.  Problem: rename a couple of symbols, and then you can't select a symbol that has been renamed.  Maybe the array controller
        // is still bound to the old collection view.  It'd be nice to get multi-select working on a glyph that has been moved... I think that
        // would solve the issue.  Is it an issue with this binding?  Yeah... I need to make sure that I get a new cView if a move has happened.
        // Maybe reloadData isn't enough.  The array controller needs to bind to the cv with the new item in it.
        // Well is that even true... I think so... it would explain the behavior anyway (not all things being selected.)
        // Well NO, the reason not all things are selected is because of shouldSelectRow and that the ac CONTENT MUST get the new item!
        // Rodan:     [runsArrayController bind:@"contentArray" toObject:workflowObject withKeyPath:@"workflowRuns" options:nil];
        // I think the problem was that it was a handshake issue and was solved by using the selection INDEXES from the coll view on the array controller.
    console.log("Binding cvArrayController " + aRow + " selectionIndexes to new cv with " + [[cv content] count] + " items");
        // This is just selection indexes... what about content?  Content goes the other way: the cv binds to the ac arranged objects.
    [cv addObserver:self forKeyPath:@"selectionIndexes" options:nil context:aRow];  // allows observeValueForKeyPath function
}

/*
    KVO (Key Value Observing) method.  This is how I trigger code when the collection view changes selection.
    References:
    1. NSKeyValueObserving Protocol Reference
    2. http://www.cocoabuilder.com/archive/cocoa/220039-nscollectionview-getting-notified-of-selection-change.html
    addObserver and implement the right method on the observer (use a new class: collectionViewObserver)
    aChange is a neato dictionary.
    aContext is the row that got clicked.
*/
- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(CPCollectionView)aCollectionView change:(CPDictionary)aChange context:(id)aContext
{
    var theClickedRow = aContext,
        newIndexSet = [aChange valueForKey:@"CPKeyValueChangeNewKey"];

    if (([newIndexSet firstIndex] !== CPNotFound))
    {
        [theOtherTableViewDelegate nullifySelection];   // Works except for the part where I add a selection to sync the two tables.  I only want to nullify
                                                        // on mouse click.  So, how do I handle that case.  Do I handle it here?  Maybe I can do that
                                                        // part without selecting.  Find the other glyph and just do the write on it!
        if (! ([[CPApp currentEvent] modifierFlags] & (CPShiftKeyMask | CPCommandKeyMask)))  //http://stackoverflow.com/questions/9268045
        {
            var i = 0,
                symbolCollections = [theGameraGlyphs symbolCollections],
                symbolCollectionsCount = [symbolCollections count];

            for (; i < symbolCollectionsCount; ++i)
            {
                if (i !== theClickedRow)
                {
                    // [cvArrayControllers[i] setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
                    [[symbolCollections[i] cvArrayController] setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
                    // The reason that we ensure that firstIndex != CPNotFound is because this line of code causes ANOTHER call to observeValueForKeyPath.
                    // So we break an infinite loop by only nullifying other views' selections if the newIndexSet has a firstIndex (which isn't true for
                    // this line's change of selection)
                    // This might cause a problem when I change the indices from the SymbolTable.  Maybe I will unbind and rebind the cv as I do that.
                    // However, I'm leaving that function till later.
                }
            }
            // This part actually gets called TWICE when once would be enough.
            // For some reason observeValueForKeyPath gets called twice when you click a new collection view.  The first aChange doesn't make sense:
            // both 'old' and 'new' contain the same indexSet.  I don't feel the need to figure what why the first change happens.
        }
    }
    // Ok, so what do?
    // if not shift*
    //   nullify selections of all other array controllers
    //   if no change and it's a single selection
    //     default (I don't feel the need to allow deselection... they can ctrl click if they really want)
    //   else
    //     default (don't implement) (let the change go through)
    // if shift
    //   default

    // It would be REALLY nice if I had that global array that was a composition of all the collection view arrays.
    // That way, on a shift click, I could ask that array controller for an index, and then make a range from there
    // to the new click.

    // Another task for this function: maintain the selection indexes of a global array controller.  OR just loop through the ones I have
    // each time someone hits enter on the text box.  If the models are looking at the same data, that SHOULD work.
}

- (void)nullifySelection
{
    var emptyIndexSet = [CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)],
        symbolCollections = [theGameraGlyphs symbolCollections],
        symbolCollectionsCount = [symbolCollections count];

    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        [[symbolCollections[i] cvArrayController] setSelectionIndexes:emptyIndexSet];
    }
}

- (BOOL)hasSelection
{
    var symbolCollections = [theGameraGlyphs symbolCollections],
        symbolCollectionsCount = [symbolCollections count];
    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        if ([[[symbolCollections[i] cvArrayController] selectionIndexes] firstIndex] !== CPNotFound)
        {
            console.log("hasSelection returning true.");
            return true
        }
    }
    console.log("hasSelection returning false.");
    return false;
}

- (void)tableView:(CPTableView)aTableView objectValueForTableColumn:(CPTableColumn)aTableColumn row:(int)aRow
// (Data source method)
{
    return [[theGameraGlyphs symbolCollectionsArrayController] arrangedObjects][aRow]; // (Ignoring the column... the table has only one column)
}

- (void)numberOfRowsInTableView:(CPTableView)aTableView
// (Data source method)
{
    return [[[theGameraGlyphs symbolCollectionsArrayController] contentArray] count];
}

- (void)tableView:(CPTableView)aTableView heightOfRow:(int)aRow
// Returns the height of a specified row.  (Delegate method.)
{
    var ac = [[CPArrayController alloc] init],
        dummyView = [[CPView alloc] initWithFrame:CGRectMake(1,1,CGRectGetWidth([aTableView bounds]),1)],
        _cv = [self _makeCollectionViewForTableView:aTableView arrayController:ac parentView:dummyView row:aRow];

    return CGRectGetHeight([_cv bounds]) + [self headerLabelHeight];
}

- (CPCollectionView)_makeCollectionViewForTableView:(CPTableView)aTableView arrayController:(CPArrayController)cvArrayController parentView:(CPView)aView  row:(int)aRow
{
    // console.log("_make for row " + aRow);
    var model = [[aTableView dataSource] tableView:aTableView objectValueForTableColumn:nil row:aRow],
        cv = [[CPCollectionView alloc] initWithFrame:CGRectMakeZero()];

    [cv setAutoresizesSubviews:NO];
    [cv setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMaxYMargin];
    [cv setMinItemSize:CGSizeMake([model maxCols] + (2 * [PhotoView inset]), [model maxRows] + (2 * [PhotoView inset]))];
    [cv setMaxItemSize:CGSizeMake([model maxCols] + (2 * [PhotoView inset]), [model maxRows] + (2 * [PhotoView inset]))];
        // Rock on: setting min and max to the same value allows me to set the itemSize exactly what I need it.
        // (Before, itemSize was getting set too large and the collectionView was always a little bit larger than its superView.
        // See CPCollectionView._computeGridWithSize.... height = MAX(aSuperviewSize.height, numberOfRows * (_minItemSize.height + _verticalMargin))
        // My collection view was getting cut off because it was larger than its superview.  Thankfully I didn't have to change CPCollectionView,
        // I just set the itemSize from here.  This way awesomely makes tableView:heightOfRow actually make sense!
    [cv setDelegate:self];
    [cv setSelectable:YES];
    [cv setAllowsMultipleSelection:YES];
    [cv setVerticalMargin:2];

    var itemPrototype = [[CPCollectionViewItem alloc] init],
        photoView = [[PhotoView alloc] initWithFrame:CGRectMakeZero()];

    [photoView setBounds:CGRectMake(0, 0, [model maxCols], [model maxRows])];
    [photoView setFrame: CGRectMake(0, 0, [model maxCols] + (2 * [PhotoView inset]), [model maxRows] + (2 * [PhotoView inset]))];

    [photoView setAutoresizesSubviews:NO];
    [photoView setAutoresizingMask:CPViewMinXMargin | CPViewMinYMargin | CPViewMaxXMargin | CPViewMaxYMargin];
    [itemPrototype setView:photoView];
    [cv setItemPrototype:itemPrototype];
    [cv bind:@"content" toObject:cvArrayController withKeyPath:@"contentArray" options:nil];

    [aView addSubview:cv];

    [cv setContent:[model glyphList]];

    return cv;
}

- (void)tableViewColumnDidResize:(CPNotification)aNotification
{
    // console.log("Resized.");
    var tableView = [aNotification object];
    [tableView noteHeightOfRowsWithIndexesChanged:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,[tableView numberOfRows])]];
        // Maybe turn off animation for the above command
    // [tableView reloadData];  // Seems to perform about the same as reloadDataForRowIndexes
    var scrollView = [[tableView superview] superview],
        visibleRows = [tableView rowsInRect:[[scrollView contentView] bounds]];
    [tableView reloadDataForRowIndexes:visibleRows columnIndexes:0];
        // see http://stackoverflow.com/questions/12067018 for other approaches
}

// This function will help with selection... find a way to pass the event to the collection view
- (void)tableView:(CPTableView)aTableView shouldSelectRow:(int)aRow
// Returns the height of a specified row
{
    var cvArrayController = [[theGameraGlyphs symbolCollections][aRow] cvArrayController];

    console.log("ShouldSelectRow: [cvArrayController selectionIndexes] count] is " + [[cvArrayController selectionIndexes] count] +
        ", [cvArrayController contentArray] count] is " + [[cvArrayController contentArray] count]);
    if ([[cvArrayController selectionIndexes] count] === [[cvArrayController contentArray] count])
    {
        // all are selected
        console.log("ShouldSelectRow: deselecting items.");
        [cvArrayController setSelectedObjects:[]];
    }
    else
    {
        console.log("ShouldSelectRow: selecting " + [[cvArrayController contentArray] count] + " items.");
        [cvArrayController setSelectedObjects:[cvArrayController contentArray]];
        // Not setting all four... hmmm.  Print selectedObjects and contentArray... try to determine why the fourth isn't set.
        console.log([cvArrayController selectedObjects]);
        console.log([cvArrayController contentArray]);  // Maybe KVC doesn't get notified by addGlyph?  But content array's count goes up I think.
    }
    return NO;
}

@end
