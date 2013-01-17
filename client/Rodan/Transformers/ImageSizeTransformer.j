@implementation ImageSizeTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    if (value != null)
    {
        if ((value / 1000000) > 1)
        {
            return ((Math.round((value / 1000000.0) * 100) / 100) + " MB" );
        }
        else if ((value / 1000) > 1)
        {
            return ((Math.round((value / 1000.0) * 100) / 100) + " KB" );
        }
        else
        {
            return (value + " B");
        }
    }
}

@end
