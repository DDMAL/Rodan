@import <Ratatosk/WLRemoteObject.j>

@implementation User : WLRemoteObject
{
    CPString    pk          @accessors;
    CPString    username    @accessors;
    CPString    firstName   @accessors;
    CPString    lastName    @accessors;
    CPArray     groups      @accessors;
    BOOL        isActive    @accessors;
    BOOL        isStaff     @accessors;
    BOOL        isSuperuser @accessors;
    CPString    email       @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['username', 'username'],
        ['firstName', 'first_name'],
        ['lastName', 'last_name'],
        ['isActive', 'is_active'],
        ['isStaff', 'is_staff'],
        ['isSuperuser', 'is_superuser'],
        ['email', 'email'],
        ['groups', 'groups']
    ];
}
@end
