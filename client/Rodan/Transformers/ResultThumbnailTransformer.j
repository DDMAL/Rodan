@import "../Models/SimpleResult.j"

@implementation ResultThumbnailTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(SimpleResult)aResult
{
    if (aResult != nil && [aResult processed])
    {
        return [aResult mediumThumbURL];
    }
    return nil;
}

@end
