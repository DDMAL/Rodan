@import "../Models/Result.j"

@implementation ResultThumbnailTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(Result)aResult
{
    if (aResult != nil && [aResult processed])
    {
        return [aResult mediumThumbURL];
    }
    return nil;
}

@end
