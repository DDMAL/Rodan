// The purpose of this transformer is to change the RunJob job_settings JSON,
//
// job_settings: [
//     {
//         default: "2bfd8910ee094ffdb82b674fad1bc6d5",
//         has_default: null,
//         rng: null,
//         name: "classifier",
//         type: "uuid"
//     },
//     {...},
//     {...}...
// ]
//
// ... into a dictionary:
//
// { "name": "default",
//   "name": "default", ... }
//

@implementation RunJobSettingsTransformer : CPObject
{

}

+ (Class)transformedValueClass
{
    return [CPMutableDictionary class];
}

- (CPArray)transformedValue:(CPArray)jsonArrayOfJobSettings
{
    var settingsCount = [jsonArrayOfJobSettings count],
        settingsDict = [[CPMutableDictionary alloc] init],
        i = 0;
    for (; i < settingsCount; ++i)
    {
        if (jsonArrayOfJobSettings[i]['name'] === @"pageglyphs")
        {
            // Special case for pageglyphs which are a UUID and not a URL, see issue #
            [settingsDict setObject:'/pageglyphs/' + jsonArrayOfJobSettings[i]['default'] forKey:@"pageglyphs"];
        }
        else
        {
            // Normal case
            [settingsDict setObject:jsonArrayOfJobSettings[i]['default'] forKey:jsonArrayOfJobSettings[i]['name']];
        }
    }
    return settingsDict;
}

@end
