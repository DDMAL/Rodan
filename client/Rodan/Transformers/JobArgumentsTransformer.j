@implementation JobArgumentsTransformer : CPObject
{
}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

- (id)transformedValue:(id)value
{
    if (value === "{}")
        return [{}];

    if ([value class] === [CPString class])
        return JSON.parse(value);

    return value;
}

- (id)reverseTransformedValue:(id)value
{
    return JSON.stringify(value);
}

- (BOOL)_isEmptyObject:(id)anObject
{
    for (var i in anObject)
    {
        return false;
    }
    return true;
}

@end
