@import <Foundation/CPNumberFormatter.j>

/**
 * Per instructions of CPNumberFormatter, subclassed for implementation.
 */
@implementation RKIntegerFormatter:CPNumberFormatter
{
}

////////////////////////////////////////////////////////////////////////////////////////////
// Public Methods
////////////////////////////////////////////////////////////////////////////////////////////
- (CPString)stringForObjectValue:(id)aObject
{
    if (aObject !== nil && [aObject class] !== nil && [aObject class].name === "CPNumber")
    {
        return [aObject stringValue];
    }
    return nil;
}

- (BOOL)getObjectValue:(idRef)aObject forString:(CPString)aString errorDescription:(CPStringRef)aError
{
    if (aString !== null)
    {
        @deref(aObject) = [aString intValue];
        return YES;
    }

    return NO;
}
@end
