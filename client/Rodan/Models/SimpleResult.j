@import <Foundation/CPObject.j>


@implementation SimpleResult : CPObject
{
    CPString    pk              @accessors;
    CPString    created         @accessors;
    CPString    updated         @accessors;
    CPString    mediumThumbURL  @accessors;
    CPString    result          @accessors;
    CPString    runJob          @accessors;
    CPString    runJobName      @accessors;
    BOOL        processed       @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    if (self = [self init])
    {
        var mapping = [
            ['created', 'created'],
            ['updated', 'updated'],
            ['mediumThumbURL', 'medium_thumb_url'],
            ['result', 'result'],
            ['runJob', 'run_job'],
            ['runJobName', 'run_job_name'],
            ['processed', 'processed']
            ];

        var i = 0,
            count = mapping.length;
        for (; i < count; i++)
        {
            var map = mapping[i];
            [self setValue:jsonObject[map[1]] forKey:map[0]];
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
