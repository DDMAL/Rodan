@implementation JobTypeTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

- (id)transformedValue:(id)value
{
    switch (value)
    {
        case 0:
            return "Non-Interactive";
            break

        case 1:
            return "Interactive";
            break;

        default:
            return "Unknown";
            break;
    }
}

@end
