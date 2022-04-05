import unittest
from MeiOutput import MeiOutput
import json


class T(unittest.TestCase):

    inJSOMR_synth = './tests/synthetic_res/classification/jsomr_output.json'
    inJSOMR_cf18 = './tests/cf18_res/classification/jsomr_output.json'
    with open(inJSOMR_synth, 'r') as f:
        jsomr_synth = json.loads(f.read())
    with open(inJSOMR_cf18, 'r') as f:
        jsomr_cf18 = json.loads(f.read())

    kwargs = {
        'max_width': 0.4,
        'max_size': 8,
        'version': 'N',
    }

    ###########
    # General
    ###########

    def test_a01_generate_synthMEI(self):
        T.mei_obj_synth = MeiOutput(T.jsomr_synth, T.kwargs)
        assert True

    def test_a02_generate_cf18MEI(self):
        T.mei_obj = MeiOutput(T.jsomr_cf18, T.kwargs)
        assert True

    ##########################
    # Relative Pitch Finding
    ##########################

    SCALE = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

    pitches_initial = [
        {
            'startPitch': ('a', '3', 'c'),
            'contour': 'u',
            'interval': 2,
        }, {
            'startPitch': ('a', '3', 'c'),
            'contour': 'u',
            'interval': 5,
        }, {
            'startPitch': ('a', '3', 'c'),
            'contour': 'u',
            'interval': 7,
        }, {
            'startPitch': ('a', '3', 'f'),
            'contour': 'd',
            'interval': 3,
        }, {
            'startPitch': ('a', '3', 'f'),
            'contour': 'd',
            'interval': 6,
        }, {
            'startPitch': ('a', '3', 'f'),
            'contour': 'd',
            'interval': 9,
        }, {
            'startPitch': ('c', '3', 'c'),
            'contour': 's',
            'interval': 1,
        }, {
            'startPitch': ('c', '3', 'c'),
            'contour': 's',
            'interval': 69,
        }
    ]

    pitches_expected = [
        ['b', '3', 'c'],
        ['e', '4', 'c'],
        ['g', '4', 'c'],

        ['f', '3', 'f'],
        ['c', '3', 'f'],
        ['g', '2', 'f'],

        ['c', '3', 'c'],
        ['c', '3', 'c'],
    ]

    def test_c01_get_relative_pitch(self):
        for i, p in enumerate(T.pitches_initial):
            newPitch = T.mei_obj._get_new_pitch(p['startPitch'], p['contour'], p['interval'])
            assert T.pitches_expected[i] == newPitch

    ##########
    # Zonify
    ##########

    # generic neume types
    glyphs = [
        {'glyph': {  # pes
            'bounding_box': {
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
                'ncols': 200},
            'name': 'neume.punctum.u2.punctum'}
         },

        {'glyph': {  # scandicus
            'bounding_box': {
                'nrows': 300,
                'ulx': 0,
                'uly': 0,
                'ncols': 300},
            'name': 'neume.punctum.u2.punctum.u2.punctum'},
         },

        {'glyph': {  # clivis
            'bounding_box': {
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
                'ncols': 200},
            'name': 'neume.punctum.d2.punctum'},
         },

        {'glyph': {  # climacus
            'bounding_box': {
                'nrows': 300,
                'ulx': 0,
                'uly': 0,
                'ncols': 300},
            'name': 'neume.punctum.d2.punctum.d2.punctum'},
         },

        {'glyph': {  # torculus
            'bounding_box': {
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
                'ncols': 300},
            'name': 'neume.punctum.u2.punctum.d2.punctum'},
         },

        {'glyph': {  # porrectus
            'bounding_box': {
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
                'ncols': 300},
            'name': 'neume.punctum.d2.punctum.u2.punctum'},
         },

        {'glyph': {  # porrectus with ligature
            'bounding_box': {
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
                'ncols': 300},
            'name': 'neume.ligature2.u2.punctum'},
         },
    ]

    # expected 'bounding boxes' for each glyph
    glyphs_zonified = [
        [       # pes
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 100,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 0,
            }
        ],
        [       # scandicus
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 200,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 100,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 200,
                'uly': 0,
            }
        ],
        [       # clivis
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 0,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 100,
            }
        ],
        [       # climacus
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 0,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 100,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 200,
                'uly': 200,
            }
        ],
        [       # torculus
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 100,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 0,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 200,
                'uly': 100,
            }
        ],
        [       # porrectus
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 0,
                'uly': 0,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 100,
                'uly': 100,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 200,
                'uly': 0,
            }
        ],
        [       # porrectus with ligature
            {
                'ncols': 200,
                'nrows': 200,
                'ulx': 0,
                'uly': 0,
            },
            {
                'ncols': 100,
                'nrows': 100,
                'ulx': 200,
                'uly': 0,
            }
        ]
    ]

    # expected contours for each glyph
    glyphs_contours = [
        # 0 = same
        #  1 = u2,  2 = u3 ...
        # -1 = d2, -2 = d3 ...
        [0, 1],
        [0, 1, 1],
        [0, -1],
        [0, -1, -1],
        [0, 1, -1],
        [0, -1, 1],
        [0, -1, 1],
    ]

    glyphs_zone_pos = [
        # ulx, uly, lrx, lry
        [[0, 0, 1, 1], [1, -1, 2, 0]],
        [[0, 0, 1, 1], [1, -1, 2, 0], [2, -2, 3, -1]],
        [[0, 0, 1, 1], [1, 1, 2, 2]],
        [[0, 0, 1, 1], [1, 1, 2, 2], [2, 2, 3, 3]],
        [[0, 0, 1, 1], [1, -1, 2, 0], [2, 0, 3, 1]],
        [[0, 0, 1, 1], [1, 1, 2, 2], [2, 0, 3, 1]],
        [[0, 0, 2, 2], [2, 0, 3, 1]],
    ]

    glyphs_zone_pos_is_positive = [
        False,
        False,
        True,
        True,
        False,
        True,
        True
    ]

    glyphs_zone_edges = [
        # xmin, xmax, ymin, ymax
        (0, 2, 0, 2),
        (0, 3, 0, 3),
        (0, 2, -1, 1),
        (0, 3, -2, 1),
        (0, 3, 0, 2),
        (0, 3, -1, 1),
        (0, 3, -1, 1),
    ]

    def test_e_01__zonify_bounding_boxes(self):
        for i, g in enumerate(T.glyphs):
            # print('\n', T.mei_obj._get_zonified_bounding_boxes(g))
            assert T.glyphs_zonified[i] == T.mei_obj._get_zonified_bounding_boxes(g)

    def test_e_02_find_numeric_contours(self):
        for i, g in enumerate(T.glyphs):
            name = g['glyph']['name'].split('.')
            num_ncs = int(len(g['glyph']['name'].split('.')) / 2)
            nc_names = list(name[2 * i: (2 * i) + 2] for i in range(0, num_ncs))

            assert T.glyphs_contours[i] == T.mei_obj._find_numeric_contours(nc_names)

    def test_e_03_find_zone_positions(self):
        for i, g in enumerate(T.glyphs):
            name = g['glyph']['name'].split('.')
            num_ncs = int(len(g['glyph']['name'].split('.')) / 2)
            nc_names = list(name[2 * i: (2 * i) + 2] for i in range(0, num_ncs))

            # print(T.mei_obj._find_zone_positions(nc_names, T.glyphs_contours[i]))
            assert T.glyphs_zone_pos[i] == T.mei_obj._find_zone_positions(nc_names, T.glyphs_contours[i])

    def test_e_04_find_zone_edges(self):
        for i, g in enumerate(T.glyphs):
            name = g['glyph']['name'].split('.')
            num_ncs = int(len(g['glyph']['name'].split('.')) / 2)
            nc_names = list(name[2 * i: (2 * i) + 2] for i in range(0, num_ncs))

            assert T.glyphs_zone_edges[i] == T.mei_obj._find_zone_edges(nc_names, T.glyphs_contours[i])

    def test_e_05_zone_pos_is_positive(self):
        for i, g in enumerate(T.glyphs_zone_pos):
            assert T.glyphs_zone_pos_is_positive[i] == T.mei_obj._zone_pos_is_positive(g)

    def test_e_06_shift_zone_pos_positive(self):
        for i, g in enumerate(T.glyphs_zone_pos):
            if not T.mei_obj._zone_pos_is_positive(g):
                g = T.mei_obj._shift_zone_pos_positive(g)
            assert T.mei_obj._zone_pos_is_positive(g)
