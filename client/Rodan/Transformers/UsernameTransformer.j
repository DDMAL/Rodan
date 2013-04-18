/*
    Takes a user object and either displays Firstname Lastname or the username if those
    have not been defined.
*/
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
            return value.first_name + " " + value.last_name;
        else
            return value.username;
    }
}

@end
