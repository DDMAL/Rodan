@implementation ArrayCountTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    if (value != nil)
    {
        return [value count];
    }
    return 0;
}

@end
