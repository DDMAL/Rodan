@implementation UsernameTransformer : CPValueTransformer
{
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    if (value)
    {
        if ((value.first_name != "") && (value.last_name != ""))
            return (value.first_name + " " + value.last_name);
        else
            return value.username;
    }
}

@end
