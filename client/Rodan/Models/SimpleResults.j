@import <Foundation/CPObject.j>


@implementation SimpleResults : CPObject
{
    CPString    created         @accessors;
    CPString    mediumThumbURL  @accessors;
    CPString    result          @accessors;
    CPString    runJob          @accessors;
    CPString    runJobName      @accessors;
    CPString    pk              @accessors;
}

- (id)initWithJson:(JSObject)jsonObject
{
    var mapping = [
        ['created', 'created'],
        ['mediumThumbURL', 'medium_thumb_url'],
        ['result', 'result'],
        ['runJob', 'run_job'],
        ['runJobName', 'run_job_name'],
        ['pk', 'url']
        ];

    var i = 0,
        count = mapping.length;
    for (; i < count; i++)
    {
        var map = mapping[i];
        [self setValue:jsonObject[map[1]] forKey:map[0]];
    }

    return self;
}
@end
