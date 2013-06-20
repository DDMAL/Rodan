// The purpose of this transformer is to change the RunJob job_settings JSON
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
// into a dictionary
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
        [settingsDict setObject:jsonArrayOfJobSettings[i]['default'] forKey:jsonArrayOfJobSettings[i]['name']];
    }
    return settingsDict;
}

@end
