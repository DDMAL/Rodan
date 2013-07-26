/*
    Glyphs have features.
    I'd rather have the features field as a CPDictionary or a javascript object, but I keep getting
    - Uncaught TypeError: Cannot read property 'info' of undefined.
    when I do [glyph setValue:x forKey:features].  Defining a Features class solves that issue.
*/

@implementation Features : WLRemoteObject
{
    CPArray  volume            @accessors;
    CPArray  ncolsFeature      @accessors;
    CPArray  area              @accessors;
    CPArray  moments           @accessors;
    CPArray  volume16regions   @accessors;
    CPArray  nholesExtended    @accessors;
    CPArray  nrowsFeature      @accessors;
    CPArray  topBottom         @accessors;
    CPArray  volume64regions   @accessors;
    CPArray  zernikeMoments    @accessors;
    CPArray  skeletonFeatures  @accessors;
    CPArray  compactness       @accessors;
    CPArray  aspectRatio       @accessors;
    CPArray  blackArea         @accessors;
    CPArray  nholes            @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['volume',            'volume'            ],
        ['ncolsFeature',      'ncols_feature'     ],
        ['area',              'area'              ],
        ['moments',           'moments'           ],
        ['volume16regions',   'volume16regions'   ],
        ['nholesExtended',    'nholes_extended'   ],
        ['nrowsFeature',      'nrows_feature'     ],
        ['topBottom',         'top_bottom'        ],
        ['volume64regions',   'volume64regions'   ],
        ['zernikeMoments',    'zernike_moments'   ],
        ['skeletonFeatures',  'skeleton_features' ],
        ['compactness',       'compactness'       ],
        ['aspectRatio',       'aspect_ratio'      ],
        ['blackArea',         'black_area'        ],
        ['nholes',            'nholes'            ]
        ];
}

- (Object)toJson
{
    // This is pretty generic and a parent class between WLRemoteObject and Features could probably be added.
    // Only though if it'd be useful.
    console.log("[Features toJson].");
    var remoteProperties = [[self class] remoteProperties],
        remotePropertiesCount = [remoteProperties count],
        js = new Object();

    for (var i = 0; i < remotePropertiesCount; i++)
    {
        var objectKey = remoteProperties[i][0],
            serverKey = remoteProperties[i][1];

        js[serverKey] = [self objectKey];
    }

    return js;
}

@end
