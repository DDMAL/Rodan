
@import <Foundation/CPObject.j>

@implementation RodanKit : CPObject

+ (CPString)version
{
    var bundle = [CPBundle bundleForClass:[self class]];

    return [bundle objectForInfoDictionaryKey:@"CPBundleVersion"];
}
@end
