/*
 * AppController.j
 * ProjectManager
 *
 * Created by You on August 2, 2011.
 * Copyright 2011, Your Company All rights reserved.
 */

@import <Foundation/CPObject.j>
@import <AppKit/CPOutlineView.j>

@import "Controllers/RPMProjectController.j"
@import "Controllers/RPMUsersWindowController.j"
@import "Controllers/RPMWorkflowController.j"

@implementation AppController : CPObject
{
    @outlet CPWindow            theWindow; //this "outlet" is connected automatically by the Cib
    @outlet CPView              theSidebar;
    @outlet CPScrollView        theScrollView;
    @outlet CPOutlineView       projectsList;
}

- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    // This is called when the application is done loading.
}

- (void)awakeFromCib
{
    // This is called when the cib is done loading.
    // You can implement this method on any object instantiated from a Cib.
    // It's a useful hook for setting up current UI values, and other things.
    
    // In this case, we want the window from Cib to become our full browser window
    [projectsList setBackgroundColor:[CPColor colorWithHexString:@"e0ecfa"]];
    
    var textColumn = [[CPTableColumn alloc] initWithIdentifier:@"TextColumn"];
    [textColumn setWidth:200.0];
    
    [projectsList setHeaderView:nil];
    [projectsList setCornerView:nil];
    [projectsList addTableColumn:textColumn];
    [projectsList setOutlineTableColumn:textColumn];
    
    items = [CPDictionary dictionaryWithObjects:[[@"glossary1"], [@"proj1", @"proj2", @"proj3"]] forKeys:[@"Glossaries", @"Projects"]];
    [projectsList setDataSource:self];
    
    [theWindow setFullPlatformWindow:YES];
}

- (id)outlineView:(CPOutlineView)outlineView child:(int)index ofItem:(id)item
{
    CPLog("outlineView:%@ child:%@ ofItem:%@", outlineView, index, item);

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

- (BOOL)outlineView:(CPOutlineView)outlineView isItemExpandable:(id)item
{
    CPLog("outlineView:%@ isItemExpandable:%@", outlineView, item);
    
    var values = [items objectForKey:item];
    return ([values count] > 0);
}

- (int)outlineView:(CPOutlineView)outlineView numberOfChildrenOfItem:(id)item
{
    CPLog("outlineView:%@ numberOfChildrenOfItem:%@", outlineView, item);

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
    CPLog("outlineView:%@ objectValueForTableColumn:%@ byItem:%@", outlineView, tableColumn, item);
    
    return item;   
}

@end
