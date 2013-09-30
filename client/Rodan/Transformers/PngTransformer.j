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

- (id)transformedValue:(id)base64WithPrefix
{
    var sep = [[self class] separator];

    return [CPData dataWithBase64:base64WithPrefix.split(sep)[1]];
}

- (id)reverseTransformedValue:(CPData)aCPData
{
    var pre = [[self class] prefix],
        sep = [[self class] separator];

    return pre.concat(sep, [aCPData base64]);
}

+ (CPString)prefix
{
    return "data:image/png;base64";
}

+ (CPString)separator
{
    return ",";
}


@end
