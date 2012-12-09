/*
 * AppController.j
 * Rodan
 *
 * Created by You on November 20, 2012.
 * Copyright 2012, Your Company All rights reserved.
 */

@import <Foundation/Foundation.j>
@import <AppKit/AppKit.j>
@import <Ratatosk/Ratatosk.j>

@import "AppController.j"


function main(args, namedArgs)
{
    // ensure this is set before doing any calls
    [WLRemoteLink setDefaultBaseURL:@""];

    CPApplicationMain(args, namedArgs);
}
