

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

+ (id)initWithSetting:(JSObject)setting
{
    var self = [self init];

    if (settings.name)
        [self setSettingName:settings.name];

    if (settings.has_default)
        [self setSettingDefault:settings.default];

    if (settings.rng)
        [self setRange:[CPArray arrayWithArray:settings.rng]];

    [self setSettingType:settings.type];

    return self;
}

@end
