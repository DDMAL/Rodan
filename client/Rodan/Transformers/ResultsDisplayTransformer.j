@implementation ResultsDisplayTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

- (id)transformedValue:(id)value
{
    if (value)
        return [value[0] thumbURL];
}

@end
