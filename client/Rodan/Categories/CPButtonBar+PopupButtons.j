@import <AppKit/CPButtonBar.j>

@implementation CPButtonBar (PopupPlusButton)

+ (id)plusPopupButton
{
    var button = [[CPPopUpButton alloc] initWithFrame:CGRectMake(0, 0, 35, 25)],
        image = [[CPTheme defaultTheme] valueForAttributeWithName:@"button-image-plus" forClass:[CPButtonBar class]];

    [button addItemWithTitle:nil];
    [[button lastItem] setImage:image];
    [button setImagePosition:CPImageOnly];
    [button setValue:CGInsetMake(0, 0, 0, 0) forThemeAttribute:"content-inset"];

    [button setPullsDown:YES];
    return button;
}

@end
