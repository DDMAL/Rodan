@import <Foundation/CPTimer.j>
@import <Foundation/CPNotification.j>


var _msInstance = nil,
    _SECONDS_DEFAULT = 10;

/**
 * Generic event timer.
 */
@implementation RKNotificationTimer : CPObject
{
    CPTimer     _msTimer;
    CPString    _msNotification;
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PUBLIC STATIC METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Schedules notification.
 */
+ (void)setTimedNotification:(float)aSeconds notification:(CPNotification)aNotification
{
    // Save/check params.
    var intervalSeconds = _SECONDS_DEFAULT;
    if (aSeconds >= 0)
    {
        intervalSeconds = aSeconds;
    }

    // Clear any existing notification timer.
    [RKNotificationTimer clearTimedNotification];

    // Create new.
    [RKNotificationTimer _getInstance]._msNotification = aNotification;
    [RKNotificationTimer _getInstance]._msTimer = [CPTimer scheduledTimerWithTimeInterval:intervalSeconds
                                                           target:[RKNotificationTimer _getInstance]
                                                           selector:@selector(_receiveTimerEvent:)
                                                           userInfo:nil
                                                           repeats:YES];

    // Fire once now.
    [[RKNotificationTimer _getInstance]._msTimer fire];
}


/**
 * Clears existing notification timer.
 */
+ (void)clearTimedNotification
{
    if ([RKNotificationTimer _getInstance]._msTimer != nil)
    {
        [[RKNotificationTimer _getInstance]._msTimer invalidate];
        [[RKNotificationTimer _getInstance]._msTimer dealloc];
    }
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PRIVATE STATIC METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Returns singleton instance.
 */
+ (id)_getInstance
{
if (!_msInstance)
    {
        _msInstance = [[RKNotificationTimer alloc] init];
    }
    return _msInstance;
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
- (id)init
{
    return self;
}


- (void)_receiveTimerEvent:(CPTimer)aCPTimer
{
    [[CPNotificationCenter defaultCenter] postNotificationName:_msNotification
                                          object:nil];
}

@end
