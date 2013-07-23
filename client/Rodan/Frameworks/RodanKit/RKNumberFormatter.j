@import <Foundation/CPNumberFormatter.j>

/**
 * Per instructions of CPNumberFormatter, subclassed for implementation.
 */
@implementation RKNumberFormatter:CPNumberFormatter
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
        var value = [aString intValue];
        if ([self minimum] != nil && [aString intValue] < [self minimum])
        {
            @deref(aObject) = [self minimum];
        }
        else if ([self maximum] != nil && [aString intValue] > [self maximum])
        {
            @deref(aObject) = [self maximum];
        }
        else
        {
            @deref(aObject) = [aString intValue];
        }
        return YES;
    }

    return NO;
}
@end
