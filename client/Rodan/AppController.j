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
@import "ProjectsController.j"


@implementation AppController : CPObject
{
    CPWindow        theWindow; //this "outlet" is connected automatically by the Cib
    CPSplitView     verticalSplitter;
    CPScrollView    scrollView;
    CPOutlineView   outlineView;
}

- (void)applicationDidFinishLaunching:(CPNotification)aNotification
{
    CPLogRegister(CPLogConsole);
    var contentView = [theWindow contentView],
        toolbar = [[CPToolbar alloc] initWithIdentifier:@"theToolbar"],
        bounds = [contentView bounds];

    [toolbar setDelegate:self];
    [toolbar setVisible:true];
    [theWindow setToolbar:toolbar];

    var verticalSplitter = [[CPSplitView alloc] initWithFrame:CGRectMake(0, 0, CGRectGetWidth([contentView bounds]), CGRectGetHeight([contentView bounds]))];
    [verticalSplitter setDelegate:self];
    [verticalSplitter setVertical:YES];
    [verticalSplitter setAutoresizingMask:CPViewWidthSizable | CPViewHeightSizable ];
    [verticalSplitter setIsPaneSplitter:YES];
    [contentView addSubview:verticalSplitter];

    var leftPaneView = [[CPView alloc] initWithFrame:CGRectMake(0, 0, 200, CGRectGetHeight([verticalSplitter bounds]))];
    [leftPaneView setBackgroundColor:[CPColor colorWithCalibratedRed:219.0 / 255.0 green:223.0 / 255.0 blue:232.0 / 255.0 alpha:1.0]];

    var scrollView = [[CPScrollView alloc] initWithFrame:CGRectMake(0.0, 0.0, CGRectGetWidth([leftPaneView bounds]), CGRectGetHeight([leftPaneView bounds]))];
    [scrollView setAutoresizingMask:CPViewHeightSizable | CPViewWidthSizable];
    [scrollView setAutohidesScrollers:YES];
    [scrollView setHasHorizontalScroller:NO];

    var projectsView = [ProjectsController initWithOutlineView:scrollView];
    [scrollView setDocumentView:[projectsView outlineView]];

    [leftPaneView addSubview:scrollView];
    // var outlineView = [[CPOutlineView alloc] initWithFrame:[scrollView bounds]];


    var mainPaneView = [[CPView alloc] initWithFrame:CGRectMake(0, 0, CGRectGetWidth([verticalSplitter bounds]) - CGRectGetWidth([leftPaneView bounds]), CGRectGetHeight([verticalSplitter bounds]))];

    [verticalSplitter addSubview:leftPaneView];
    [verticalSplitter addSubview:mainPaneView];



    [theWindow setFullPlatformWindow:YES];
}

@end
