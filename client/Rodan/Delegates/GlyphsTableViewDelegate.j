@import "../Views/PhotoView.j"
@import "../Views/ViewWithObjectValue.j"
@import "../Models/SymbolCollection.j"
@import "../Models/GameraGlyphs.j"

@implementation GlyphsTableViewDelegate : CPObject
{
    @outlet CPArrayController       symbolCollectionArrayController;
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
    // Perhaps we don't need this initialize function any more
    [theTableView reloadData];
}

- (CPMutableArray)writeSymbolName:(CPString)newName
{
    /// ----------------  ALGORITHM PSEUDOCODE -----------------
    // If there's no symbolCollection yet with that name
    //   Make one, and an array controller for it
    // For each array controller's selection
    //   Remove the glyph from its current place
    //   Change its name
    //   Add it to its new place

    // That's basically all that happens... in addition to some cleanup of the selections, and some simple stuff with the table view,
    // and a bug fixed with rearrangeObjects.
    // Bindings:  Every time a glyph list is changed (added or removed to,) a cvArrayController must be rebound
    //            Every time a symbolCollection is added or removed, symbolCollectionArrayController must be rebound

    // Returns: an array of the glyphs that were written.
    /// -------------------------------------------------------

    var newBinIndex = [self _makeSymbolCollectionForName:newName],
        symbolCollections = [theGameraGlyphs symbolCollections],
        symbolCollectionsCount = [symbolCollections count],
        allSelectedObjects = [[CPMutableArray alloc] init];

    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        var cvArrayController = [symbolCollections[i] cvArrayController],
            selectedObjects = [cvArrayController selectedObjects],
            selectedGlyphsInRow = [[[theGameraGlyphs symbolCollections][i] glyphList] objectsAtIndexes:[cvArrayController selectionIndexes]],
            // Confirm again that [cvArrayController selectedObjects] wouldn't do the trick... I believe it would now because the transformer's addGlyph
            // now touches the cvArrayController
            selectedGlyphsInRowCount = [selectedGlyphsInRow count];
        [allSelectedObjects addObjectsFromArray:selectedGlyphsInRow];

        if (i === newBinIndex)
        {
            // We don't need to do any writes to glyphs already in the new bin
            continue;
        }

        for (var j = 0; j < selectedGlyphsInRowCount; j++)
        {
            var glyph = selectedGlyphsInRow[j];
            [[theGameraGlyphs symbolCollections][i] removeGlyph:glyph];  // Do this with KVO (SC -> Glyph)
            [glyph writeSymbolName:newName];
            [glyph makeAllDirty];
            [glyph ensureSaved];
            [[theGameraGlyphs symbolCollections][newBinIndex] addGlyph:glyph];  // Do this with KVO (GG -> Glyph)... however the SC MUST get notified... so hopefuly when GG->Glyph removes the observer it's not too early.
                                                                                // This is where the OO model might be better, but I bet the KVO is robust enough that all observers will get notified.
        }

        [cvArrayController bind:@"contentArray" toObject:[theGameraGlyphs symbolCollections][i] withKeyPath:@"glyphList" options:nil];  // Do this with model (removeGlyph)
        [cvArrayController setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];  // Samesies
    }

    [[symbolCollections[newBinIndex] cvArrayController] bind:@"contentArray" toObject:symbolCollections[newBinIndex] withKeyPath:@"glyphList" options:nil];  // Do this with model (addGlyph)
    [[symbolCollections[newBinIndex] cvArrayController] setSelectedObjects:allSelectedObjects];  // Keep this right here, not with a notification

    var a_symbol_was_removed = false;

    for (var i = 0; i < [symbolCollections count] ; ++i)
    {
        if ([[symbolCollections[i] glyphList] count] === 0)
        {
            a_symbol_was_removed = true;
            [symbolCollections removeObjectAtIndex:i];  // Do this with KVO (GG -> SC)
            // [cvArrayControllers removeObjectAtIndex:i];  // Won't be necessary since the parallel arrays are no longer needed (removing the symbolCollection is all)
            --i;
        }
    }

    if (a_symbol_was_removed)
        [symbolCollectionArrayController bind:@"content" toObject:theGameraGlyphs withKeyPath:@"symbolCollections" options:nil];  // Do this with KVO (GG -> SC)

    console.log("Finished write, reloading data.");
    [theTableView reloadData];
    return allSelectedObjects;
}

/*
    addGlyph:  Adds the glyph to the model and keeps the corresponding cv array controller happy
*/
// - (void)addGlyph:(Glyph)aGlyph toIndex:(int)anIndex
// {
//     [[theGameraGlyphs symbolCollections][newBinIndex] addGlyph:glyph];
//     [cvArrayControllers[newBinIndex] bind:@"contentArray" toObject:[theGameraGlyphs symbolCollections][newBinIndex] withKeyPath:@"glyphList" options:nil];
// }

- (int)_makeSymbolCollectionForName:(CPString)newName
{
    var symbolCollections = [theGameraGlyphs symbolCollections],
        symbolCollectionsCount = [symbolCollections count],
        bin_already_exists = false,
        newBinIndex = 0;

    for (var i = 0; i < symbolCollectionsCount; ++i)
    {
        newBinIndex = i;
        if ([symbolCollections[i] symbolName] === newName)
        {
            bin_already_exists = true;
            break;
        }
        else if ([symbolCollections[i] symbolName] > newName)
        {
            break;
        }
    }

    if (! bin_already_exists)
    {
        var newSymbolCollection = [[SymbolCollection alloc] init];
        [newSymbolCollection setSymbolName:newName];
        [symbolCollections insertObject:newSymbolCollection atIndex:newBinIndex];  // Do it without referencing theGameraGlyphs(?)
        [symbolCollectionArrayController bind:@"content" toObject:theGameraGlyphs withKeyPath:@"symbolCollections" options:nil];  // doesn't actually need to be bound yet
    }

    return newBinIndex;
}

- (void)close
{
    [symbolCollectionArrayController setContent:[]];
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
        // So... what about making this view SMALLER.  Then, the collection view will try to fit a smaller space.  Make aView big enough to handle the spill.
        // Then, that difference amount, will just be 1x not (number_of_rows_in_collection_view)x
    // console.log("parentView's old frame height: " + String(CGRectGetHeight([aView bounds]) - [self headerLabelHeight]));
    // console.log("parentView's new frame height: " + CGRectGetHeight(_collectionViewBoundsForRow[aRow]));
    // [parentView setFrame:CGRectMake(0, [self headerLabelHeight], CGRectGetWidth([aView bounds]), CGRectGetHeight(_collectionViewBoundsForRow[aRow]))];
        // Ok, some success.  What I'm doing is giving the collection view a parent view and setting that view's height.  (Before I would set that view's height very large,
        // to a large, calculated, height where there'd be no cutoff.  That caused the cells to be enormous in the pageglyphs view.)  Now I set the parent view's height
        // smaller... but there's cutoff... so I will try to get the coll. view to draw like this, and then grow the parent view without causing the coll. view to redraw.
        // (Crosses fingers.)  I believe that the parentView is causing the cutoff and not the tableView's rowHeight.

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
        //
    console.log("Binding cvArrayController " + aRow + " selectionIndexes to new cv with " + [[cv content] count] + " items");
        // This is just selection indexes... what about content?  Content goes the other way: the cv binds to the ac arranged objects.
    [cv addObserver:self forKeyPath:@"selectionIndexes" options:nil context:aRow];  // allows observeValueForKeyPath function
    // [parentView setFrame:CGRectMake(0, [self headerLabelHeight], CGRectGetWidth([aView bounds]), CGRectGetHeight([aView bounds]) - [self headerLabelHeight])];  // Needs to happen later.
        // I don't know if it'll even work.  But if it does, I could write a loop to go through each 'parentView' and grow it a little.
        // But it makes sense that willDisplayView needs to return before I grow parentView.  Could I override reloadData?  I'd have to subclass CPTableView, but I could
        // easily do it in the delegate.
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
    return [symbolCollectionArrayController arrangedObjects][aRow]; // (Ignoring the column... the table has only one column)
}

- (void)numberOfRowsInTableView:(CPTableView)aTableView
// (Data source method)
{
    return [[symbolCollectionArrayController contentArray] count];
}

- (void)tableView:(CPTableView)aTableView heightOfRow:(int)aRow
// Returns the height of a specified row.  (Delegate method.)
{
    var ac = [[CPArrayController alloc] init],
        dummyView = [[CPView alloc] initWithFrame:CGRectMake(1,1,CGRectGetWidth([aTableView bounds]),1)],
        _cv = [self _makeCollectionViewForTableView:aTableView arrayController:ac parentView:dummyView row:aRow],
        symbolCollection = [[aTableView dataSource] tableView:aTableView objectValueForTableColumn:nil row:aRow],
        glyphWidth = [symbolCollection maxCols] + (2 * [PhotoView inset]),
        glyphCount = [[symbolCollection glyphList] count],
        tableWidth = CGRectGetWidth([aTableView bounds]),
        number_of_rows_in_collection_view = Math.ceil((glyphWidth * glyphCount) / tableWidth),  // Try [_cv numberOfRows]
        bottom_image_frame = [[_cv subviews][[[_cv subviews] count] - 1] frame],
        bottom_of_last_image = CGRectGetMaxY(bottom_image_frame),
        cell_spacing_neglected_by_collection_view = bottom_of_last_image - CGRectGetHeight([_cv bounds]);

    return CGRectGetHeight([_cv bounds]) + cell_spacing_neglected_by_collection_view + [self headerLabelHeight];

    // Let me explain the ridiculousness here.
    // First, read http://stackoverflow.com/questions/7504546 and understand that we need to build a dummy collection
    // view to solve the chicken&egg problem: we need to build a dummy coll view so that we can assign a row height,
    // which we need to do before building the coll view that goes in the table, because that view needs the row height
    // to render itself.
    // Now, that approach ALMOST worked, but it seems that when the coll. view underestimates its size (fogetting about the
    // space between cells, and if there is more than one row, then there is cutoff.  If there are a lot of rows, there is a
    // lot of cutoff.)
    // This problem is partly solved by reading the max y coordinate of the last image in the collection view, and using that
    // in the row height.  Unfortunately, you need to repeat that algorithm for each row in the collection view, because the
    // view rearranges itself and continues to spill out to be larger than the row.  You need to calculate the number of rows
    // in the collection view, and iterate the correction that number of times.
    // Now, it turns out each such iteration adds the SAME amount, so instead of iterating, I'll do it once, and then add
    // according to how much height was added.  Again, that amount is the difference between the cv's reported height and
    // the height found by looking at the bottom of the last image.
    // I can't think of another algorithm that solves this problem, so that's what I implemented

    // There seems to be a minor width issue.  See if the coll view's width is actually wider than it should be... Consider building it in a smaller view (?)
    //   (?) because that never worked for me before, I think it must be laid out inside the tableView's aView... which I don't think gives me leeway...
    //   unless I call setFrame on the collView.  Worth a shot.
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
        // My collection view was getting cut off because it was larger than the superView.  Thankfully I didn't have to change CPCollectionView,
        // I just set the itemSize from here.
    [cv setDelegate:self];
    [cv setSelectable:YES];
    [cv setAllowsMultipleSelection:YES];
    [cv setVerticalMargin:2];

    var itemPrototype = [[CPCollectionViewItem alloc] init],
        photoView = [[PhotoView alloc] initWithFrame:CGRectMakeZero()];

    [photoView setBounds:CGRectMake(0, 0, [model maxCols], [model maxRows])];
    [photoView setFrame: CGRectMake(0, 0, [model maxCols] + (2 * [PhotoView inset]), [model maxRows] + (2 * [PhotoView inset]))];

    // Hmmm... each photoView is given the same Bounds here.  I might need autosizing to accomplish what I want.
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
