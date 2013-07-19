@implementation PhotoView : CPImageView  // Why is it a CPImageView??? _imageView is the imageView
/*
    PhotoView implements functions required by the collection view
    (setSelected and setRepresented)
    see http://280north.com/learn/tutorials/scrapbook-tutorial-2/
*/
{
    CPImageView _imageView;
}

// The collection view doesn't call 'init' on its PhotoViews... maybe because they're views and not a models,
// so don't bother trying to implement init.  Also, even though the GlyphsTableViewDelegate
// calls init, the collection view ends up not using the view given to it, it makes its own.  (The GlyphsTableView
// one is a prototype.  (My first instinct was to make 'inset' a field, but making it a class method has the
// benefit of actually working.)

/*
    [PhotoView inset] returns the number of cells that border the imageView.  So the PhotoView is 10 cells
    larger than the imageView on all four sides.  The PhotoView darkens upon selection, and this margin is
    necessary in order for the user to see that a cell has been selected.
*/
+ (id)inset
{
    return 10;
}

- (void)setSelected:(BOOL)isSelected
{
    [self setBackgroundColor:isSelected ? [CPColor grayColor] : nil];
}

- (void)setRepresentedObject:(id)anObject
{
    var inset = [[self class] inset];

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
    // [_imageView setAutoresizingMask:CPViewMinXMargin | CPViewMinYMargin ];  // Well, Y looks okay.  But I can't quite get autosizing to work right.
    [_imageView setFrame:CGRectMake(inset, inset, [anObject nCols], [anObject nRows])];
    [_imageView setAutoresizesSubviews:NO];
    [_imageView setAutoresizingMask:CPViewMinXMargin | CPViewMaxXMargin | CPViewMinYMargin | CPViewMaxYMargin];
}

@end
