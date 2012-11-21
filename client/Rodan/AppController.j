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

    var mainPaneView = [[CPView alloc] initWithFrame:CGRectMake(0, 0, CGRectGetWidth([verticalSplitter bounds]) - CGRectGetWidth([leftPaneView bounds]), CGRectGetHeight([verticalSplitter bounds]))];

    [verticalSplitter addSubview:leftPaneView];
    [verticalSplitter addSubview:mainPaneView];


    var request = [CPURLRequest requestWithURL:"http://localhost:8000/api/v1/project?format=json"];
    [request setHTTPMethod:"GET"];

    var connection = [CPURLConnection connectionWithRequest:request delegate:self];

    [theWindow setFullPlatformWindow:YES];
}

- (id)jsonCallback
{
    console.log("What what callback!");
}

- (void)connection:(CPURLConnection)connection didFailWithError:(id)error
{
    console.log("Oops, Error");
}

- (void)connection:(CPURLConnection)connection didReceiveResponse:(CPURLResponse)response
{
    console.log("Reeespooonse!");
    console.log([response statusCode]);
}

- (void)connection:(CPURLConnection)connection didReceiveData:(CPString)data
{
    console.log("Data!");
    var j = JSON.parse(data);
    for (var i = j.objects.length - 1; i >= 0; i--)
    {
        var p = [Project projectWithObject:j.objects[i]];
        console.log(p);
    };
}


@end
