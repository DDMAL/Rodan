@implementation RunJobStatusTransformer : CPValueTransformer
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
        case -1:
            return "Failed";
            break

        case 0:
            return "Not running";
            break

        case 1:
            return "Running";
            break;

        case 2:
            return "Waiting for input";
            break;

        case 3:
            return "Run once waiting";
            break;

        case 4:
            return "Has finished";
            break;

        default:
            return "Unknown";
            break;
    }
}
@end
