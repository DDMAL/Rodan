@import <Foundation/CPObject.j>
@import "../Models/SimpleResult.j"


@implementation SimplePage : CPObject
{
    CPString    pageName    @accessors;
    CPNumber    pageOrder   @accessors;
    CPString    pk          @accessors;
    CPArray     results     @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    var mapping = [
        ['pk', 'url'],
        ['pageName', 'name'],
        ['pageOrder', 'page_order'],
        ['results', 'results'],
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

    return self;
}
@end
