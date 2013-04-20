/*
 * RodanKit.j
 * RodanKit
 */

/*
    USAGE

    Put an @import of every source file in your framework here. Users of the framework
    can then simply import this file instead of having to know what the individual
    source filenames are.
*/
@import <Foundation/CPObject.j>

@implementation RodanKit : CPObject

+ (CPString)version
{
    var bundle = [CPBundle bundleForClass:[self class]];

    return [bundle objectForInfoDictionaryKey:@"CPBundleVersion"];
}

@end
