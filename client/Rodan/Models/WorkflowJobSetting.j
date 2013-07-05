

@implementation WorkflowJobSetting : CPObject
{
    CPNumber    settingDefault @accessors;
    BOOL        hasDefault     @accessors;
    CPArray     range          @accessors;
    CPString    settingType    @accessors;
    CPString    settingName    @accessors;
    CPString    choices        @accessors;
    BOOL        visibility     @accessors;
}

- (id)init
{
    var self = [super init];
    if (self)
    {
    }

    return self;
}

+ (CPArray)propertyMap
{
    return [
        ['settingDefault', 'default'],
        ['hasDefault', 'has_default'],
        ['range', 'rng'],
        ['settingType', 'type'],
        ['settingName', 'name'],
        ['choices', 'choices'],
        ['visibility', 'visibility']
    ];
}

+ (id)initWithSetting:(JSObject)setting
{
    var self = [[WorkflowJobSetting alloc] init];
    [self setSettingName:setting.name];
    [self setSettingType:setting.type];

    // Ugly hack to overcome JSON poorly handling floats.
    if (setting.type == 'float' || setting.type == 'real')
    {
        var floatString = setting.default;
        [self setSettingDefault:[floatString floatValue]];
    }
    else
    {
        [self setSettingDefault:setting.default];
    }

    // Determine visibility.
    if ("visibility" in setting)
    {
        [self setVisibility:setting.visibility];
    }
    else
    {
        [self setVisibility:YES];
    }

    if (setting.rng)
        [self setRange:[CPArray arrayWithArray:setting.rng]];

    if (setting.choices)
        [self setChoices:[CPArray arrayWithArray:setting.choices]];


    return self;
}

@end
