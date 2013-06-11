@import <Foundation/CPObject.j>
@import "../Models/SimpleResult.j"


@implementation SimplePage : CPObject
{
    CPString    pk              @accessors;
    CPString    pageName        @accessors;
    CPNumber    pageOrder       @accessors;
    CPArray     results         @accessors;
    CPString    mediumThumbURL  @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    if (self = [self init])
    {
        var mapping = [
            ['pk', 'url'],
            ['pageName', 'name'],
            ['pageOrder', 'page_order'],
            ['results', 'results'],
            ['mediumThumbURL', 'medium_thumb_url'],
            ];

        var i = 0,
            count = mapping.length;

        for (; i < count; i++)
        {
            var map = mapping[i],
                resultArray = [];
            if (map[1] == "results")
            {
                var j = 0,
                    resCount = jsonObject['results'].length;

                for (; j < resCount; j++)
                {
                    var res = [[SimpleResult alloc] initWithJson:jsonObject['results'][j]];
                    [resultArray addObject:res];
                }
                [self setValue:resultArray forKey:map[0]];
            }
            else
            {
                [self setValue:jsonObject[map[1]] forKey:map[0]];
            }
        }
    }
    return self;
}

#pragma mark CPObject

- (CPString)description
{
    return "<" + [self class] + " " + [self UID] + (pk ? " " + pk : "") + ">";
}
@end
