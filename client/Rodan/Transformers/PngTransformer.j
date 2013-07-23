@implementation PngTransformer : CPObject //See WLRemoteTransformers.j in Ratatosk
{

}
+ (BOOL)allowsReverseTransformation
{
    return NO;
}
+ (Class)transformedValueClass
{
    return [CPData class];
}
- (id)transformedValue:(id)value
{
    return [CPData dataWithBase64:value];
}
@end
