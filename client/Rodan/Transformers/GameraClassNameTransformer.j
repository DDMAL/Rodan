@implementation GameraClassNameTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    var splitString = [value componentsSeparatedByString:"."];
    if ([splitString count] > 1)
    {
        theName = [[splitString lastObject] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        return [theName capitalizedString];
    }
    return value;
}

@end
