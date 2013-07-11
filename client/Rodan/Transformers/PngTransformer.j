@implementation PngTransformer : CPObject //See WLRemoteTransformers.j in Ratatosk
{

}

+ (BOOL)allowsReverseTransformation
{
    return YES;
}

+ (Class)transformedValueClass
{
    return [CPData class];
}

- (id)transformedValue:(id)base64
{
    return [CPData dataWithBase64:base64];
}

- (id)reverseTransformedValue:(CPData)aCPData
{
    return [aCPData base64];
}

@end
