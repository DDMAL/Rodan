@import <Ratatosk/WLRemoteObject.j>

@implementation ClassifierSetting : WLRemoteObject
{
    CPString        pk                          @accessors;
    CPString        uuid                        @accessors;
    CPString        name                        @accessors;
    CPString        fileUrl                     @accessors;
    CPString        project                     @accessors;
    CPString        producer                    @accessors;
    id              fitness                     @accessors;
    CPString        optimizationStartedAt       @accessors;
    CPString        optimizationFinishedAt      @accessors;
    CPString        creator                     @accessors;
    CPString        created                     @accessors;
    CPString        updated                     @accessors;
}

+ (CPArray)remoteProperties
{
    return [
        ['pk',                         'url'                        ],
        ['uuid',                       'uuid'                       ],
        ['name',                       'name'                       ],
        ['fileUrl',                    'file_url'                   ],
        ['project',                    'project'                    ],
        ['producer',                   'producer'                   ],
        ['fitness',                    'fitness'                    ],
        ['optimizationStartedAt',      'optimizationStartedAt'      ],
        ['optimizationFinishedAt',     'optimizationFinishedAt'     ],
        ['creator',                    'creator'                    ],
        ['created',                    'created'                    ],
        ['updated',                    'updated'                    ]
    ];
}

- (CPString)remotePath
{
    return [self pk];
}

@end
