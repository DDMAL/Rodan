// Credit/Reference: http://www.chandlerkent.com/2009/12/10/Building-a-Sidebar-With-CPOutlineView.html

// TODO: Rename this because it's not an OutlineView anymore.
@implementation SymbolOutlineDelegate : CPObject
{
            CPDictionary    items;
    @outlet CPOutlineView   theOutlineView;
    @outlet CPScrollView    scrollView;
    @outlet CPTableColumn   textColumn;
    @outlet CPArrayController symbolArrayController;
}

- (void)awakeFromCib
{
    [scrollView setBackgroundColor:[CPColor colorWithHexString:@"e0ecfa"]];
    [scrollView setAutohidesScrollers:YES];

    [theOutlineView setHeaderView:nil];
    [theOutlineView setCornerView:nil];

    [theOutlineView setOutlineTableColumn:textColumn];

    items = [CPDictionary dictionaryWithObjects:[[@"glossary 1"], [@"proj 1", @"proj 2", @"proj 3"]]
                          forKeys:[@"Glossaries", @"Projects"]];
    [theOutlineView setDataSource:self];  // This tells the outlineView to look at SymbolOutlineController
                                          // for the methods it needs.
}

// ---------------------------- DELEGATE METHODS --------------------------------------
- (id)outlineView:(CPOutlineView)outlineView child:(int)index ofItem:(id)item
{
    //CPLog("outlineView:%@ child:%@ ofItem:%@", outlineView, index, item);

    if (item === nil)
    {
        // item is nil for the top level of the tree... so return key[index]
        // (this is the text for the index'th top level entry)
        var keys = [items allKeys];
        //console.log([keys objectAtIndex:index]);
        return [keys objectAtIndex:index];
    }
    else
    {
        // if item is not nil, then we have our key already, because we're in a subtree
        var values = [items objectForKey:item];
        //console.log([values objectAtIndex:index]);
        return [values objectAtIndex:index];
    }
    // For an array of symbol names, this function would be O(n)
    // I think that we need to make a dict (a keyed array) out of symbol names.
    // so symbols['neume'] would be all the strings that start with neume
    // I could just do O(n) stuff all the time...
    // - sort the names alphabetically
    // - for i; i<count; ++i:  look for a string with name 'item'
    //   Actually: binary search would help
    // - when you find it, go 'index' more items down and return it if it's still a 'neume'
    // It would be so much nicer if I could key by symbol name... but what would be the
    // value?  An array of all the neumes?  That's not possible for a normal dict.
    // I think that I could one-shot build a tree thing out of lists
    // - the leaves could be glyphs
    // - that could help with the 'selection' problem.  If a leaf is selected, I'll have
    // the glyph object and can tell the other view what to select.
    // If a node is selected, then select all of the leaves of it.
    // What about using regexes to match... like ^clef or ^clef.c etc.
    // That would be fast, if the symbols were like lines in a file and if I could use grep.
    // I think I need to find a tree data structure... a multi linked list
    // I could do tree.add(glyph) and it would get put into the proper spot.
    // The link names would be symbol names, like root.child... ?
    // What about XML?
    // We could get up to 18000 glyphs... does it have to be super efficient?
    // Each list would be a dict.  Each node can have glyph leaves.

    // If I could just do it in python: have one giant string with newlines between
    // the symbol names and use re.search to give back the arrays...
    // I can see why Gamera doesn't let you select a node in the tree and
    // have it match with the collection view.
    // theClassifier has an array of Glyphs, which aren't even keyed by symbol name.

    // I don't think we need a tree.  If it's flat, you still get all the info out
    // from the naming.  You sort alphebetically and the tree is obvious.
    // How about just make it a list on the left??  You can then get the Glyphs
    // out in O(n) just by comparing names.  You lose the 'hide' functionality of
    // the outline view, but I don't think that's a big loss... you can use the scroll
    // bar.

    // Note: display each symbol name once, and consider a (count) in brackets.
    // I'll sleep on it.

    // If I do want an outline view, dictionaries could do the trick
    //{
    //    'neume': {'virga': {}
    //    }
    //}

    // One main problem with the list idea is that the '.' loses it's meaning:
    // it's just strings then that follow a pattern.  The dots are meaningful
    // to Gamera and we need to convey that.

    // What if I omit text, to convey meaning, in a way that doesn't waste rows...
    // (You will only be able to drag and drop into bins that already have a neume.)
}

- (BOOL)outlineView:(CPOutlineView)outlineView isItemExpandable:(id)item
{
    //CPLog("outlineView:%@ isItemExpandable:%@", outlineView, item);

    var values = [items objectForKey:item];  // returns 0 if item isn't a top level key
                                             // and nonzero if it is
                                             // (only top level keys are expandable)
    //console.log(([values count] > 0));
    return ([values count] > 0);
}

- (int)outlineView:(CPOutlineView)outlineView numberOfChildrenOfItem:(id)item
/* Return how many children an item has */
{
    //CPLog("outlineView:%@ numberOfChildrenOfItem:%@", outlineView, item);

    if (item === nil)
    {
        // item is nil for the top level of the tree, so return the number of
        // top level categories.
        return [items count];
    }
    else
    {
        // We're in a subtree, so return the number of children of the given key
        var values = [items objectForKey:item];
        return [values count];
    }
}

- (id)outlineView:(CPOutlineView)outlineView objectValueForTableColumn:(CPTableColumn)tableColumn byItem:(id)item
/* Return the text for the cell for the given item */
{
    //CPLog("outlineView:%@ objectValueForTableColumn:%@ byItem:%@", outlineView, tableColumn, item);

    //console.log(item);

    return item;
}
@end
