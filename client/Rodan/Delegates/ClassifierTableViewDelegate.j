@import "../Views/PhotoView.j"
@import "../Views/ViewWithObjectValue.j"
@import "../Models/SymbolCollection.j"
@import "../Models/Classifier.j"

@implementation ClassifierTableViewDelegate : CPObject
{
    @outlet CPArrayController   symbolCollectionArrayController;
            CPMutableArray      cvArrayControllers  @accessors;
            int                 headerLabelHeight   @accessors;
            int                 photoViewInset      @accessors;
    @outlet CPTableView         theTableView;
}

- (void)init
{
    self = [super init];
    if (self)
    {
        [self setHeaderLabelHeight:20];
        [self setPhotoViewInset:10];
        // [[CPNotificationCenter defaultCenter] addObserver:self selector:@selector(scrollViewContentBoundsDidChange:) name:CPViewBoundsDidChangeNotification object:self.scrollView.contentView];
        [self setCvArrayControllers:[[CPArray alloc] init]];
    }

    return self;
}

- (void)initializeTableView
{
    console.log("Initializing table view!");
    // var i = 0,
    //     // glyphs = [aClassifier glyphs],
    //     glyphs = [classifierGlyphsArrayController arrangedObjects],  // I think this may break write... I need to always use the model directly
    //     // glyphs = [classifierGlyphsArrayController contentArray],
    //     glyphs_count = [glyphs count],
    //     prevGlyphName = nil,
    //     symbolCollectionArray = [[CPMutableArray alloc] init],
    //     symbolCollection = nil;

    // for (i = 0; i < glyphs_count; ++i)
    // {
    //     var glyphName = [glyphs[i] idName];
    //     if (prevGlyphName === nil || prevGlyphName !== glyphName)
    //     {
    //         symbolCollection = [[SymbolCollection alloc] init];
    //         [symbolCollection setSymbolName:glyphName];
    //         [symbolCollectionArray addObject:symbolCollection];
    //     }
    //     [symbolCollection addGlyph:glyphs[i]];
    //     prevGlyphName = glyphName;
    // }

    // [symbolCollectionArrayController setContent:symbolCollectionArray];

    var nSymbols = [[symbolCollectionArrayController contentArray] count];
    [cvArrayControllers initWithCapacity:nSymbols];
    for (var j = 0; j < nSymbols; ++j)
    {
        [cvArrayControllers addObject:[self _makeAndBindCvArrayControllerToSymbolCollection:[symbolCollectionArrayController contentArray][j]]];  // gets added at index j
    }
    console.log(cvArrayControllers);

    [theTableView reloadData];
}

- (void)writeSymbolName:(CPString)newName
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
    /// -------------------------------------------------------

    var symbolCollectionArray = [symbolCollectionArrayController arrangedObjects],
        symbolCollectionArray_count = [symbolCollectionArray count],
        bin_already_exists = false,
        newBinIndex = 0;

    // TODO: Optimize, maybe with filters
    // Assume sorted
    for (; newBinIndex < symbolCollectionArray_count; ++newBinIndex)
    {
        if ([symbolCollectionArray[newBinIndex] symbolName] === newName)
        {
            bin_already_exists = true;
            break;
        }
        else if ([symbolCollectionArray[newBinIndex] symbolName] > newName)
        {
            break;
        }
    }

    if (! bin_already_exists)
    {
        // Make a bin (a symbolCollection).
        var newSymbolCollection = [[SymbolCollection alloc] init];
        [newSymbolCollection setSymbolName:newName];
        console.log("Adding new symbolCollection with name " + [newSymbolCollection symbolName] + ".");
        [symbolCollectionArrayController insertObject:newSymbolCollection atArrangedObjectIndex:newBinIndex];  // Maintains sort of arrangedObjects
            // Maybe I should call rearrangeObjects on symbolCollectionArrayController more often... then I shouldn't sort on the server
        [cvArrayControllers insertObject:[self _makeAndBindCvArrayControllerToSymbolCollection:newSymbolCollection] atIndex:newBinIndex];
      //   // [theTableView noteNumberOfRowsChanged];  // Breaks it... and doesn't seem to be necessary as we reloadData anyway, which gets the # of rows right.
    }
    var cvArrayControllers_count = [cvArrayControllers count],
        initiallySelectedObjects = [[CPMutableArray alloc] init];
    for (var i = 0; i < cvArrayControllers_count; ++i)
    {
        var selectedObjects = [cvArrayControllers[i] selectedObjects];
        [initiallySelectedObjects addObjectsFromArray:selectedObjects];
        // Try it as a one-shot (?)  I think it's too tough because of the moving around of glyphs.
        // [cvArrayControllers[i] remove:self];  // Removes the controller's selected objects from the controller's collection
        // Perhaps, for style, I should quit using symbolCollectionArrayController completely (except for updateMaxes)
        // while([selectedObjects count] > 0)
        while([[cvArrayControllers[i] selectedObjects] count] > 0)
        {
            // var glyph = selectedObjects[0];
            var glyph = [cvArrayControllers[i] selectedObjects][0];
            [cvArrayControllers[i] setSelectedObjects:[[cvArrayControllers[i] selectedObjects] removeObjectAtIndex:0]];
            [cvArrayControllers[i] removeObject:glyph];  // Note that this also removes the glyph from the symbolCollection's glyphList (same model)
                // Perhaps cvArrayControllers should be renamed to glyphArrayControllers, and glyphList to glyphArray.
            if ([[[symbolCollectionArrayController arrangedObjects][i] glyphList] count] === 0)
            {
                [symbolCollectionArrayController removeObjectAtArrangedObjectIndex:i];  // will shift left everything, so [i] is now the next item
                [cvArrayControllers removeObjectAtIndex:i];  // I'm glad that the collection view doesn't complain about this.
                --cvArrayControllers_count;  // Used by for loop
                --i;  // Hmmm, is --i necessary?  I don't think so***, I think I can continue with the same i (which is the next i)
                    // I guess I did it to counteract the for loop's ++. I think the code will work either way in most cases, so I'm going to remove it.
                    // (With the -- in, then the while loop will just iterate again in the way that the for loop normally would.)
                    // Maybe I don't need the while... and it can be one loop.  Nah, the while is for selectedObjects, the for is for table rows
                    // ***ACTUALLY I believe it is.  The while loop will certainly finish on this go around (this must be the last item in
                    // selectedObjects because it was the last item in the glyphList.  The next thing we want the for loop to
                    // do, is process selectedObjects from the SAME i, because the next row to process, will be the row with the same i.
                if (newBinIndex > i)
                {
                    --newBinIndex;
                }
                // [theTableView noteNumberOfRowsChanged];
            }
            console.log("Writing glyph, old name: " + [glyph idName] + " new name: " + newName);
            console.log(glyph);
            [glyph writeSymbolName:newName];
            [[symbolCollectionArrayController arrangedObjects][newBinIndex] addGlyph:glyph];
            // [cvArrayControllers[newBinIndex] addObject:glyph];  // Alternative way... possibly be more KVC compliant
            // [symbolCollectionArrayController arrangedObjects][newBinIndex] updateMaxes];  // Alternative way
            [cvArrayControllers[newBinIndex] setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];  // Gets set later (TODO: don't bother)
                // Experiment with setSelectedInsertedObjects
            // selectedObjects = [selectedObjects removeObjectAtIndex:0];  // Try going through the controller
            // [cvArrayControllers[i] removeSelectedObjects];
        }
    }

    [cvArrayControllers[newBinIndex] rearrangeObjects];  // Makes things work. (setSelectedObjects :contentArray was not working before I did this)
    // [cvArrayControllers[newBinIndex] setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
    [cvArrayControllers[newBinIndex] setSelectedObjects:initiallySelectedObjects];
    [theTableView reloadData];
}

// - (void)          writeSymbolName                                :(CPString)        newName
- (CPArrayController)_makeAndBindCvArrayControllerToSymbolCollection:(SymbolCollection)aSymbolCollection
{
    var cvArrayController = [[CPArrayController alloc] init];
    [cvArrayController bind:@"contentArray" toObject:aSymbolCollection withKeyPath:@"glyphList" options:nil];  // try contentArray!
    // [cvArrayControllers[j] bind:@"content" toObject:symbolCollectionArray[j] withKeyPath:@"glyphList" options:nil];  // also works
    [cvArrayController setAvoidsEmptySelection:NO];
    [cvArrayController setPreservesSelection:YES];  // Seems important for the loop that moves (removes) glyphs one at a time
    [cvArrayController rearrangeObjects];
    // rearrangeObjects is just a good thing to do.  (I do it later, and doing it now makes it so that things don't get all rearranged.)
    // It kills the selection though.
    [cvArrayController setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
    return cvArrayController;
}

- (void)close
{
    [symbolCollectionArrayController setContent:[]];  // Also need to kill all of the subArrays.
      // Also need to unset all of the symbolCollections... the labels are bound to that model, and not through the array controller
      // Maybe the label ought to be bound through the array controller... like with objectValue (via the table's binding)
        // Use a dict of arrays keyed by symbol name.
    // var enumerator = [cvArrayControllerDict objectEnumerator],
    //     cvArrayController;
    // while (cvArrayController = [enumerator nextObject])
    // {
    //     [cvArrayController setContent:[]];
    // }
    // [cvArrayControllerDict removeAllObjects];
    [theTableView noteNumberOfRowsChanged];
    [theTableView reloadData];
    // Ok.  I didn't even need the cvArrayControllerDict for this.  Wow.
    // So my first approach was sort of a 'binding' style approach in which I was hoping that the table view would
    // empty when I killed the content of the array controller.  However, I'm not using binding, I'm using a coded
    // approach, because of all of the hooplah with the collection view and the row height.  So the best binding
    // could do would be to empty the coll views and labels, but the tableView would still sort of be there (and the
    // scroll bar,) so it's much better to just tell the tableView what to do explicitly (reloadData... after erasing
    // the data).  Side note: the SymbolOutline uses the former approach (binding.)
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
        symbolName = [symbolCollection symbolName],  // If I use binding, I don't need this variable
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
    [parentView setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMaxYMargin];
    [aView addSubview:parentView];
    [parentView setFrame:CGRectMake(0, [self headerLabelHeight], CGRectGetWidth([aView bounds]), CGRectGetHeight([aView bounds]) - [self headerLabelHeight])];
    var cv = [self _makeCollectionViewForTableView:aTableView arrayController:cvArrayControllers[aRow] parentView:parentView row:aRow];
    // [cv bind:@"selectionIndexes" toObject:cvArrayControllers[aRow] withKeyPath:@"selectionIndexes" options:nil];
    [cv setSelectionIndexes:[cvArrayControllers[aRow] selectionIndexes]];  // This should allow you to scroll down and back and have the selection persist
        // Now... when did cvArrayControllers[aRow] selectionIndexes get erased!
        // Maybe the binding isn't working... or maybe the array controller
    [cvArrayControllers[aRow] bind:@"selectionIndexes" toObject:cv withKeyPath:@"selectionIndexes" options:nil];
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
}

- (void)observeValueForKeyPath:(CPString)aKeyPath ofObject:(CPCollectionView)aCollectionView change:(CPDictionary)aChange context:(id)aContext
// KVO (Key Value Observing) method.  This is how I trigger code when the collection view changes selection.
// References:
// 1. NSKeyValueObserving Protocol Reference
// 2. http://www.cocoabuilder.com/archive/cocoa/220039-nscollectionview-getting-notified-of-selection-change.html
// addObserver and implement the right method on the observer (use a new class: collectionViewObserver)
// aChange is a neato dictionary.
// aContext is the row that got clicked.
{
    // console.log("observeValueForKeyPath");

    var theClickedRow = aContext;
    // Check if the new indexSet is empty.
    var newIndexSet = [aChange valueForKey:@"CPKeyValueChangeNewKey"];
    if (([newIndexSet firstIndex] !== CPNotFound) && ! ([[CPApp currentEvent] modifierFlags] & (CPShiftKeyMask | CPCommandKeyMask)))  //http://stackoverflow.com/questions/9268045
    {
        // console.log("Nullifying the selection on all other rows.");
        var i = 0,
            nArrayControllers = [cvArrayControllers count];
        for (; i < nArrayControllers; ++i)
        {
            if (i !== theClickedRow)
            {
                [cvArrayControllers[i] setSelectionIndexes:[CPIndexSet indexSetWithIndexesInRange:CPMakeRange(0,0)]];
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
        glyphWidth = [symbolCollection maxCols] + (2 * [self photoViewInset]),
        glyphCount = [[symbolCollection glyphList] count],
        tableWidth = CGRectGetWidth([aTableView bounds]),
        number_of_rows_in_collection_view = Math.ceil((glyphWidth * glyphCount) / tableWidth),
        bottom_image_frame = [[_cv subviews][[[_cv subviews] count] - 1] frame],
        bottom_of_last_image = CGRectGetMaxY(bottom_image_frame),
        cell_spacing_neglected_by_collection_view = bottom_of_last_image - CGRectGetHeight([_cv bounds]);
    return CGRectGetHeight([_cv bounds]) + cell_spacing_neglected_by_collection_view * number_of_rows_in_collection_view + [self headerLabelHeight];
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

- (void)recheck_heights:(CPView)aCvParentView
{
    var _cv = [aCvParentView subviews][0];
    console.log("---In recheck_heights!---");
    console.log("parent view height: " + CGRectGetHeight([aCvParentView frame]));
    console.log("cv height: " + CGRectGetHeight([_cv frame]));
    console.log("calculate from last image: " + CGRectGetMaxY([[_cv subviews][[[_cv subviews] count] - 1] frame]));
    console.log("---Out recheck_heights!---");
    return;
}

- (CPCollectionView)_makeCollectionViewForTableView:(CPTableView)aTableView arrayController:(CPArrayController)cvArrayController parentView:(CPView)aView  row:(int)aRow
{
    // console.log("_make for row " + aRow);
    var model = [[aTableView dataSource] tableView:aTableView objectValueForTableColumn:nil row:aRow],
        cv = [[CPCollectionView alloc] initWithFrame:CGRectMakeZero()];
    [cv setAutoresizesSubviews:NO];
    [cv setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable | CPViewMinXMargin | CPViewMaxXMargin | CPViewMaxYMargin];
    [cv setMinItemSize:CGSizeMake(0,0)];  // Aha!  Now that the PhotoView has a frame, this works.  (the size isn't determined by this.)
    [cv setMaxItemSize:CGSizeMake(10000, 10000)];
    [cv setDelegate:self];
    [cv setSelectable:YES];
    [cv setAllowsMultipleSelection:YES];
    var itemPrototype = [[CPCollectionViewItem alloc] init],
        photoView = [[PhotoView alloc] initWithFrame:CGRectMakeZero() andInset:[self photoViewInset]];
    [photoView setBounds:CGRectMake(0,0,[model maxCols],[model maxRows])];
    [photoView setFrame:CGRectMake(0,0,[model maxCols] + (2 * [photoView inset]), [model maxRows] + (2 * [photoView inset]))];
    [photoView setAutoresizesSubviews:NO];
    [photoView setAutoresizingMask:CPViewMinXMargin | CPViewMinYMargin | CPViewMaxXMargin | CPViewMaxYMargin];
    // var glyphListArrayController = [[[CPArrayController alloc] init] setContent:[model glyphList]];
    // [photoView bind:@"toolTip" toObject:glyphListArrayController withKeyPath:@"arrangedObjects" options:nil];  // doesn't work.
    [itemPrototype setView:photoView];
    [cv setItemPrototype:itemPrototype];
    // [cv bind:@"content" toObject:cvArrayController withKeyPath:@"arrangedObjects" options:nil];
    [cv bind:@"content" toObject:cvArrayController withKeyPath:@"contentArray" options:nil];
        // I'm having an issue where selecting a moved glyph doesn't work.
        // I thought it was because the collection view was binding to arrangedObjects, which wasn't getting added to while
        // contentArray was.  For now, I'm going to rule that out by binding to contentArray.  contentArray is the glyphList.

    [aView addSubview:cv];
    // [cvArrayController setContent:[model glyphList]];
        // I think this erases my selection indexes... but I do it to kick the collection view to display...
        // I think that I'll start a pattern of BINDING LATER (after content is set,) and just kicking the view with setContent
        // The binding handles CHANGES, but doesn't need to handle the initialization, because it constrains the order of operation too much.
        // Careful about changing this though... it'll affect the row height calculation.
        // That will be fixed by using the same array controller from the row height (in fact, just delete that argument.)
    [cv setContent:[model glyphList]];  // Hopefully the binding still works, I'll have to test that later.
    // [cv bind:@"content" toObject:cvArrayController withKeyPath:@"contentArray" options:nil];  // Tried kicking the collectionView by binding again, doesn't work.
        // Recall: I had to interrupt the pattern of ONLY BINDING and NOT CALLING SetContent because that required that
        // I setContent of the array controller AFTER the view has been bound.  However, the view has to be rebuilt whenever you
        // scroll past it, so I cannot setContent of the array controller that often!  It erases the selection!  That, in short,
        // is why I need to both BIND and setContent.
        // Ack... I think this causes write to work only once, I end up writing to this copied glyph!!!
        // Ideas:  Make sure to use the array controller's 'selectionIndexes' instead of 'selectedObjects'
        //  ... well, that doesn't fix anything... I'd still be writing the wrong glyph.
        //  Hmmm, the selectedObjects are those of the cv, but maybe I can query the ac's contentArray with selectionIndexes.
        //  (Hopefully, the ac's contentArray remains the right objects while the selectedObjects end up being this copy, which is
        //  is why write stops getting to the server.  TODO.)
        // Another idea is to search for the right glyph by comparing pngData.
        // Actually, this doesn't even make a copy, I'm not getting this yet.  I still need to find where the glyphs with different UIDs
        // from the classifier come from.
        // Remember, the problem is that theClassifier gets new glyphs, which the array controllers keep the same glyphs!
        // Maybe there's a way to get the cv to work without calling setContent... try reading CollectionView docs to look for alternatives.
    // console.log("New glyph UID range: " = )

    // console.log("_make returning cv for row: " + aRow + " of height: " + CGRectGetHeight([cv frame]));
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
    console.log("ShouldSelectRow: [[cvArrayControllers[aRow] selectionIndexes] count] is " + [[cvArrayControllers[aRow] selectionIndexes] count] +
        ", [[cvArrayControllers[aRow] contentArray] count] is " + [[cvArrayControllers[aRow] contentArray] count]);
    if ([[cvArrayControllers[aRow] selectionIndexes] count] === [[cvArrayControllers[aRow] contentArray] count])
    {
        // all are selected
        console.log("ShouldSelectRow: deselecting items.");
        [cvArrayControllers[aRow] setSelectedObjects:[]];
    }
    else
    {
        console.log("ShouldSelectRow: selecting " + [[cvArrayControllers[aRow] contentArray] count] + " items.");
        [cvArrayControllers[aRow] setSelectedObjects:[cvArrayControllers[aRow] contentArray]];
        // Not setting all four... hmmm.  Print selectedObjects and contentArray... try to determine why the fourth isn't set.
        console.log([cvArrayControllers[aRow] selectedObjects]);
        console.log([cvArrayControllers[aRow] contentArray]);  // Maybe KVC doesn't get notified by addGlyph?  But content array's count goes up I think.
    }
    return NO;
}
// Hmmm deselect of a single element?  Not needed as much as the collection views talking to eachother.
// Persistent selection is just fine (only deselect when a new thing is selected...)
// but I want a more global selection object.  When a second collection view is clicked, then I need to deselect from the first
// collection view, AND when a second is clicked with shift clicked, I need to retain the selection.
// I need a really global array controller... that is just all of the cvArrayControllers in series... so the collectionViews
// are bound to the little array controllers... I don't think I can bind them to a subArray of the global one... so all that code
// will stay... so I need to write a wrapper/handler that responds to every change in selection of any array controller...
// maybe I can bind...
// The handler should subscribe to ALL changes in selection (the controller must have a selectionDidChange,)... then it can also
// have full control of what happens: it can deselect all selections in the other controllers if shift isn't pressed, etc.  Then
// the text box can take its cues from the global controller.  Call it SelectionController.  It can have the TableViewDelegate and
// the SymbolTableDelegate.  It won't need the table view, because the collectionViews are bound to the array controllers, (so they
// won't need to be kicked.)  It only needs the symbolTable's array controller because it can calculate everything it needs from the
// selection<Symbol>.name.
// Well... I'm not sure that the array controller has such a notification, but the collection views do!  I'll just set them all
// to have the same delegate!
@end
