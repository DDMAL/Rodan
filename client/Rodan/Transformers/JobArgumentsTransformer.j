@import "../Models/WorkflowJobSetting.j"

@implementation JobArgumentsTransformer : CPObject
{
}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

+ (Class)transformedValueClass
{
    return [CPArray class];
}

- (id)transformedValue:(id)values
{
    // values should be a string
    console.log("Pre-transformed values");
    var c = values.length,
        returnArray = [];

    while (c--)
    {
        [returnArray addObject:[WorkflowJobSetting initWithSetting:values[c]]];
    }
    console.log(returnArray);
    return returnArray;
}

- (id)reverseTransformedValue:(id)values
{
    // values should be an array
    console.log("Reverse transformed values");
    var reversedSettings = [],
        propertyMap = [WorkflowJobSetting propertyMap],
        c = values.length;

    while (c--)
    {
        var obj = values[c],
            retObj = {};
        for (var i = 0; i < propertyMap.length; i++)
        {
            retObj[propertyMap[i][1]] = obj[propertyMap[i][0]];
        };
        [reversedSettings addObject:retObj];
    }

    // should return a string
    console.log(JSON.stringify(reversedSettings));
    return @"" + JSON.stringify(reversedSettings);
}

// - (BOOL)_isEmptyObject:(id)anObject
// {
//     for (var i in anObject)
//     {
//         return false;
//     }
//     return true;
// }

@end
