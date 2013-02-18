@import <AppKit/CPCollectionView.j>
@import "../Transformers/GameraClassNameTransformer.j"


@implementation WorkflowCollectionView : CPCollectionView
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

- (id)initWithCoder:(CPCoder)aCoder
{
    self = [super initWithCoder:aCoder]
    if (self)
    {
        console.log("Initializing");
    }
    return self;
}

- (CPCollectionViewItem)newItemForRepresentedObject:(id)anObject
{
    var item = [super newItemForRepresentedObject:anObject],
        view = [item view];

    console.log("New Item for Represented Object called for " + anObject);

    [view bind:@"jobName"
          toObject:anObject
          withKeyPath:@"jobName"
          options:[CPMutableDictionary dictionaryWithObject:GameraClassNameTransformer forKey:CPValueTransformerNameBindingOption]];

    [view setBackgroundColor:[CPColor whiteColor]];
    return item;
}

@end
