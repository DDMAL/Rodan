@implementation RetryFailedRunJobsTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (BOOL)transformedValue:(id)value
{
    return value > 0;
}

@end
