/*
 * AppController.j
 * Rodan
 *
 * Created by You on November 20, 2012.
 * Copyright 2012, Your Company All rights reserved.
 */

@import <Foundation/CPObject.j>
@import <AppKit/AppKit.j>
@import "Project.j"


@implementation AppController : CPObject
{
                CPWindow    theWindow; //this "outlet" is connected automatically by the Cib
    @outlet     CPToolbar   theToolbar;
    @outlet     CPView      scopeBar;
}

- (id)awakeFromCib
{
    CPLogRegister(CPLogConsole);
    CPLog("awakeFromCib");
}


- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    CPLog("Application Did Finish Launching");
    CPLog(theToolbar);
    var contentView = [theWindow contentView],
        bounds = [contentView bounds];

    [theToolbar setDelegate:self];
    [theToolbar setVisible:true];

    [theWindow setToolbar:theToolbar];
    [theWindow setFullPlatformWindow:YES];

    CPLog([scopeBar]);
}

@end
