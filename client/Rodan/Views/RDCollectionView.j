@import <AppKit/CPCollectionView.j>

@implementation RDCollectionView : CPCollectionView
{

}

- (id)init
{
    if (self = [super init])
    {
        console.log("Initializing");
    }
    return self;
}

- (CPCollectionViewItem)newItemForRepresentedObject:(id)anObject
{
    var item = [super newItemForRepresentedObject:anObject],
        view = [item view];

    console.log("newItemForRepresentedObject");
    console.log(anObject);
    // [view setBackgroundColor:[CPColor whiteColor]];

    // [view bind:@"jobName"
    //       toObject:anObject
    //       withKeyPath:@"jobName"
    //       options:nil];

    // [view bind:@"hoursPerWeek"
    //       toObject:anObject
    //       withKeyPath:@"hoursPerWeek"
    //       options:nil];

    return item;
}

@end
