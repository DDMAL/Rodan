/*
    Takes a user object and either displays Firstname Lastname or the username if those
    have not been defined.
*/
@implementation UsernameTransformer : CPValueTransformer
{
}

+ (Class)transformedValueClass
{
    return [CPString class];
}

+ (BOOL)allowsReverseTransformation
{
    return NO;
}

- (id)transformedValue:(id)value
{
    if (value)
    {
        if ((value.firstName != "") && (value.lastName != ""))
            return value.firstName + " " + value.lastName;
        else
            return value.username;
    }
}

@end
