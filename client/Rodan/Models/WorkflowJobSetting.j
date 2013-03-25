

@implementation WorkflowJobSetting : CPObject
{
    CPNumber    settingDefault @accessors;
    BOOL        hasDefault     @accessors;
    CPArray     range          @accessors;
    CPString    settingType    @accessors;
    CPString    settingName    @accessors;
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
        ['settingName', 'name']
    ];
}

+ (id)initWithSetting:(JSObject)setting
{
    var self = [[WorkflowJobSetting alloc] init];

    [self setSettingName:setting.name];
    [self setSettingDefault:setting.default];

    if (setting.rng)
        [self setRange:[CPArray arrayWithArray:setting.rng]];

    [self setSettingType:setting.type];

    return self;
}

@end
