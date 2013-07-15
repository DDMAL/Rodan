@import "Classifier.j"
@import "PageGlyphs.j"
@import "Features.j"

@implementation Glyph : WLRemoteObject
{
    CPString      pk              @accessors;
    CPString      uuid            @accessors;
    CPString      ulx             @accessors;
    CPString      uly             @accessors;
    CPString      nRows           @accessors;
    CPString      nCols           @accessors;
    CPString      idState         @accessors;
    CPString      idName          @accessors;
    CPString      idConfidence    @accessors;
    CPString      featureScaling  @accessors;
    Features      features        @accessors;
    CPData        pngData         @accessors;
    Classifier    classifier      @accessors;
    PageGlyphs    pageGlyphs      @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk', 'url'],
        ['uuid', 'uuid'],
        ['ulx', 'ulx'],
        ['uly', 'uly'],
        ['nRows', 'nrows'],
        ['nCols', 'ncols'],
        ['idState', 'id_state'],
        ['idName', 'id_name'],
        ['idConfidence', 'id_confidence'],
        ['featureScaling', 'feature_scaling'],
        ['features', 'features'],
        ['pngData', 'data']
    ];
}

- (CPString)remotePath
{
    return [self pk];
    // Note: you can't POST a new glyph.
    // Glyphs are made by connected component analysis on the server.
}

- (id)initWithJson:(JSObject)jsonObject
{
    // Takes JSON and makes a glyph object.  Uses remoteProperties to
    // index the values out of the JSON dictionary.
    var self = [self init];

    if (self)
    {
        [self setClassifier:nil];
        [self setPageGlyphs:nil];

        var remotePropertiesCount = [[Glyph remoteProperties] count],
            map = [Glyph remoteProperties];

        for (var i = 0; i < remotePropertiesCount; i++)
        {
            var objectKey = map[i][0],
                serverKey = map[i][1];

            if (objectKey === 'pngData')
            {
                [self setValue:[CPData dataWithBase64:jsonObject[serverKey]] forKey:objectKey];
            }
            else if (objectKey === 'features')
            {
                [self setValue:[[Features alloc] initWithJson:jsonObject[serverKey]] forKey:objectKey];
            }
            else
            {
                [self setValue:jsonObject[serverKey] forKey:objectKey];
            }
        }
    }

    return self;
}

+ (CPArray)objectsFromJson:(CPArray)jsonArrayOfGlyphs
{
    var glyphsCount = [jsonArrayOfGlyphs count],
        outArray = [];

    for (var i = 0; i < glyphsCount; ++i)
    {
        var glyph = [[Glyph alloc] initWithJson:[jsonArrayOfGlyphs objectAtIndex:i]];
        [outArray addObject:glyph];
    };

    return outArray;
}

+ (CPArray)objectsToJson:(CPArray)aGlyphArray
{
    var outArray = [],
        glyphsCount = [aGlyphArray count],
        map = [Glyph remoteProperties],
        mapCount = [map count];

    for (var i = 0; i < glyphsCount; ++i)
    {
        var JsonObject = new Object();
        // Dynamically add properties to the object using the server names
        for (var j = 0; j < mapCount; ++j)
        {
            var objectKey = map[j][0],
                serverKey = map[j][1];
            if (serverKey !== 'data')
            {
                JsonObject[serverKey] = aGlyphArray[i][objectKey];
            }
            else  //TODO: ensure that 'save' doesn't require the members to be converted to strings.
            {
                JsonObject[serverKey] = [aGlyphArray[i][objectKey] base64];
            }
        }
        [outArray addObject:JsonObject];
    }

    return outArray;
}

- (void)writeSymbolName:(CPString)newName
{
    [self setIdState:@"Manual"];
    [self setIdName:newName];
    [self setIdConfidence:@"1.000000"];
}

- (BOOL)isEqualTo:(Glyph)glyph
{
    return [self ulx] === [glyph ulx] && [self uly] === [glyph uly] &&
           [self nRows] === [glyph nRows] && [self nCols] === [glyph nCols] &&
           [[self pngData] data] === [[glyph pngData] data];
}

@end
