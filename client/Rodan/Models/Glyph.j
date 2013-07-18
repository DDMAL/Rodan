@import <Ratatosk/WLRemoteTransformers.j>
@import <Ratatosk/WLRemoteObject.j>

@import "Classifier.j"
@import "PageGlyphs.j"
@import "Features.j"
@import "../Transformers/PngTransformer.j"

@implementation Glyph : WLRemoteObject
{
    CPString        pk              @accessors;
    CPString        uuid            @accessors;
    CPString        ulx             @accessors;
    CPString        uly             @accessors;
    CPString        nRows           @accessors;
    CPString        nCols           @accessors;
    CPString        idState         @accessors;
    CPString        idName          @accessors;
    CPString        idConfidence    @accessors;
    CPString        featureScaling  @accessors;
    Features        features        @accessors;
    CPData          pngData         @accessors;
    CPString        classifierPk    @accessors;
    CPString        pageGlyphsPk    @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk',             'url'             ],
        ['uuid',           'uuid'            ],
        ['ulx',            'ulx'             ],
        ['uly',            'uly'             ],
        ['nRows',          'nrows'           ],
        ['nCols',          'ncols'           ],
        ['idState',        'id_state'        ],
        ['idName',         'id_name'         ],
        ['idConfidence',   'id_confidence'   ],
        ['featureScaling', 'feature_scaling' ],
        ['features',       'features',       [WLForeignObjectTransformer forObjectClass:Features]],
        ['pngData',        'data',           [[PngTransformer alloc] init]],
        ['classifierPk',   'classifier_url'  ],
        ['pageGlyphsPk',   'pageglyphs_url'  ]
    ];
}

- (CPString)remotePath
{
    return [self pk];
    // Note: you can't make a glyph on the client and post it.
    // Glyphs are made solely by connected component analysis on the server.
}

- (id)initWithJson:(JSObject)jsonObject
{
    [WLRemoteObject setDirtProof:YES];

    if (self = [super initWithJson:jsonObject])
    {
        [WLRemoteObject setDirtProof:NO];
    }

    return self;
}

// Maybe I won't need objectsToJson if I use the transformers right.
+ (CPArray)objectsToJson:(CPArray)aGlyphArray
{
    var outArray = [],
        glyphsCount = [aGlyphArray count],
        map = [Glyph remoteProperties],
        mapCount = [map count];

    for (var i = 0; i < glyphsCount; ++i)
    {
        var JsonObject = new Object();

        for (var j = 0; j < mapCount; ++j)
        {
            var objectKey = map[j][0],
                serverKey = map[j][1];

            if (objectKey === 'pngData')
            {
                JsonObject[serverKey] = [aGlyphArray[i][objectKey] base64];
            }
            else if (objectKey === 'features')
            {
                JsonObject[serverKey] = [aGlyphArray[i][objectKey] toJson];
            }
            else
            {
                JsonObject[serverKey] = aGlyphArray[i][objectKey];
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
