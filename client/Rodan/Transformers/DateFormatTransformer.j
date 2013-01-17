@implementation DateFormatTransformer : CPValueTransformer
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
        var dt = new Date(value);

        return (dt.getFullYear() +
            "-" + ("0" + (dt.getMonth() + 1)).slice(-2) +  //pad with leading 0's
            "-" + dt.getDate());
    }
}

@end
