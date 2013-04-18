/*
    The GameraClassNameTransformer takes a dot-separated gamera module name,
    e.g., "gamera.threshold.to_foo" and displays it as a human-readable name,
    "To Foo".
*/
@implementation GameraClassNameTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    // `value` may sometimes be null. If so, just return it.
    if (!value)
        return value

    var splitString = [value componentsSeparatedByString:"."];
    if ([splitString count] > 1)
    {
        var theName = [[splitString lastObject] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        return [theName capitalizedString];
    }
    return value;
}

@end
