@implementation ByteCountTransformer : CPValueTransformer
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
        return [CPByteCountFormatter stringFromByteCount:value
                                     countStyle:CPByteCountFormatterCountStyleFile];
    }
    return value;
}

@end
