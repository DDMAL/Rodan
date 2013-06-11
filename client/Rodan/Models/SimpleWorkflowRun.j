@import <Foundation/CPObject.j>
@import "../Models/SimplePage.j"


@implementation SimpleWorkflowRun : CPObject
{
    CPString    pk          @accessors;
    CPString    workflow    @accessors;
    CPNumber    run         @accessors;
    BOOL        testRun     @accessors;
    CPArray     pages       @accessors;
    CPString    created     @accessors;
    CPString    updated     @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    if (self = [self init])
    {
        var mapping = [
            ['pk', 'url'],
            ['workflow', 'workflow'],
            ['run', 'run'],
            ['testRun', 'test_run'],
            ['pages', 'pages'],
            ['created', 'created'],
            ['updated', 'updated']
            ];

        var i = 0,
            count = mapping.length;

        for (; i < count; i++)
        {
            var map = mapping[i],
                pageArray = [];

            if (map[1] === "pages")
            {
                var j = 0,
                    pageCount = jsonObject['pages'].length;

                for (; j < pageCount; j++)
                {
                    var page = [[SimplePage alloc] initWithJson:jsonObject['pages'][j]];
                    [pageArray addObject:page];
                }
                [self setValue:pageArray forKey:map[0]];
            }
            else
            {
                console.log()
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
