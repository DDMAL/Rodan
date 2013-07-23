@implementation PhotoView : CPImageView
/*
PhotoView implements functions required by the collection view
(setSelected and setRepresented)
see http://280north.com/learn/tutorials/scrapbook-tutorial-2/
*/
{
    CPImageView _imageView;
    int inset @accessors;
}
- (id)initWithFrame:(id)aFrame andInset:(int)anInset
{
    self = [super initWithFrame:aFrame];
    [self setInset:anInset];
    // console.log("[self inset] from initWithFrame: " + [self inset]);  // Works... but inset is null later
    return self;
}
- (void)setSelected:(BOOL)isSelected
{
    [self setBackgroundColor:isSelected ? [CPColor grayColor] : nil];
}
- (void)setRepresentedObject:(id)anObject
{
    if (!_imageView)
    {
        _imageView = [[CPImageView alloc] initWithFrame:CGRectMakeZero()];  // set the frame later (images don't seem to get added if I do it here)
        [_imageView setImageScaling:CPScaleNone];
        // [_imageView setImageAlignment:CPImageAlignCenter];   // I'm doing this by hand (setting frames)
                                                                // although, that'll look funny where there are images of different sizes... so this would be better
                                                                // to get working.
        [_imageView setBackgroundColor:[CPColor redColor]];
        [self addSubview:_imageView];
    }
    [_imageView setImage:[[CPImage alloc] initWithData:[anObject pngData]]];
    // Commented code: trying to get autosizing to work.  This might allow me to resize more efficiently.
    // [_imageView setFrame:CGRectMake(10,10,[anObject nCols],[anObject nRows])];  // inset by 10 (half of 20... which is harcoded elsewhere)
    // [_imageView setFrame:CGRectMake(0,0,[anObject nCols], [anObject nRows])];
    // console.log("self inset (in setRepresented): " + [self inset]);  //null
    // [_imageView setAutoresizingMask:CPViewMinXMargin | CPViewMinYMargin ];  // Well, Y looks okay.  It might work better I do it manually.
    // console.log("self inset: " + [self inset]);  // TODO: null!  Why is inset null!
    // [_imageView setFrame:CGRectMake([self inset],[self inset],[anObject nCols],[anObject nRows])];
    [_imageView setFrame:CGRectMake(10,10,[anObject nCols],[anObject nRows])];
    [_imageView setAutoresizesSubviews:NO];
    [_imageView setAutoresizingMask:CPViewMinXMargin | CPViewMaxXMargin | CPViewMinYMargin | CPViewMaxYMargin];
}
@end
