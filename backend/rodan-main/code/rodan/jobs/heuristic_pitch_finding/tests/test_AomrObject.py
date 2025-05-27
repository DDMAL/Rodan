import unittest
from AomrObject import AomrObject
from gamera.core import load_image


class T(unittest.TestCase):

    # def __init__(self):
    inImage = './tests/res/CF18_Staff.png'
    inGameraXML = './tests/res/CF18_Classified.xml'

    image = load_image(inImage)
    kwargs = {
        'lines_per_staff': 4,
        'staff_finder': 0,
        'staff_removal': 0,
        'binarization': 1,
        'discard_size': 12,
    }

    aomr_obj = None

    ###########
    # General
    ###########

    def test_a01_generate_aomr_obj(self):
        T.aomr_obj = AomrObject(self.image, **self.kwargs)
        assert True

    def test_a02_get_page_properties(self):
        T.page_props = T.aomr_obj.get_page_properties()
        assert True

    #################
    # Staff Finding
    #################

    def test_b01_find_staves(self):
        T.aomr_obj.find_staves()
        T.staves, T.interpolated_staves = T.aomr_obj.get_staves()
        assert True

    def test_b02_sequential_points(self):
        # all points in a line are ordered by x position from left to right
        for i, staff in enumerate(T.staves):
            for j, line in enumerate(staff['line_positions']):
                for k, pt in enumerate(line[1:]):
                    if not pt[0] > line[k][0]:
                        # points out of order
                        assert False

        assert True

    def test_b03_staves_within_page(self):

        for i, staff in enumerate(T.staves):
            if staff['coords'][2] > T.page_props['bounding_box']['ncols'] \
                    or staff['coords'][3] > T.page_props['bounding_box']['nrows']:
                # staff outside of page boundaries
                assert False

        assert True

    #######################
    # Interpolation Tests
    #######################

    def test_c01_interpolation_grabbed_previous_points(self):
        # check all original points
        for i, staff in enumerate(T.staves):
            for j, line in enumerate(staff['line_positions']):
                for pt in line:
                    if pt not in T.interpolated_staves[i]['line_positions'][j]:
                        # point does not remain in interpolated line
                        assert False
        assert True

    def test_c02_interpolated_all_points(self):
        # check all interpolated points
        for i, staff in enumerate(T.interpolated_staves):
            for j, line in enumerate(staff['line_positions']):
                for pt in line:
                    if not pt[0] or not pt[1]:
                        # missing points
                        assert False

        assert True

    def test_c03_find_right(self):
        tests = [None] * 4

        tests[0] = T.aomr_obj._find_right_pt([(1, 1), (False, False), (2, 2), (3, 3), (4, 4)], 0)
        tests[1] = T.aomr_obj._find_right_pt([(1, 1), (False, False), (False, False), (3, 3), (4, 4)], 0)
        tests[2] = T.aomr_obj._find_right_pt([(1, 1), (False, False), (False, False), (False, False), (4, 4)], 0)
        tests[3] = T.aomr_obj._find_right_pt([(1, 1), (False, False), (False, False), (False, False), (False, False)], 0)

        assert tests == [2, 3, 4, False]

    def test_c04_interpolated_ys_within_edges(self):
        for i, staff in enumerate(T.interpolated_staves):
            for j, line in enumerate(staff['line_positions']):
                original_line = T.staves[i]['line_positions'][j]

                for k, pt in enumerate(line[1:-1]):
                    if pt not in original_line:  # interpolated points should never be a max or min

                        slope_down = (pt[1] <= line[k - 1][1] and pt[1] >= line[k + 1][1])
                        slope_up = (pt[1] >= line[k - 1][1] and pt[1] <= line[k + 1][1])

                        if not (slope_down or slope_up):
                            assert False

        assert True

    ######################
    # Find Closest Staff
    ######################

    def test_d01_find_distance_between_points(self):

        points = [[(0, 0), (10, 10)],
                  [(2, 2), (6, 6)],
                  [(10, 7), (5, 8)],
                  [(400, 73), (23, 900)]]

        distances = [200, 32, 26, 826058]

        for i, (p1, p2) in enumerate(points):
            assert T.aomr_obj._find_distance_between_points(p1, p2) == distances[i] ** 0.5

    def test_d02_find_distance_between_line_and_point(self):

        lines = [[(0, 10), (5, 10)],
                 [(1000, 4500), (2500, 4500)],
                 [(2000, 2500), (1000, 2500)],
                 [(1600, 2000), (1600, 3000)]]

        points = [(0, 0),
                  (10, 10),
                  (400, 400),
                  (1600, 1600),
                  (3200, 3200),
                  (6400, 6400)]

        distances = [[10.000, 5.000, 555.090, 2252.137, 4514.878, 9040.360],
                     [4609.772, 4597.847, 4143.669, 2900.000, 1476.482, 4338.202],
                     [2692.582, 2679.589, 2184.032, 900.000, 1389.244, 5879.625],
                     [2561.249, 2547.194, 2000.0, 400.0, 1612.451, 5882.176]]

        for i, (p1, p2) in enumerate(lines):
            for j, p3 in enumerate(points):

                value = str(T.aomr_obj._find_distance_between_line_and_point(p1, p2, p3)).split('.')
                approx_result = float(value[0] + '.' + value[1][:3])

                assert distances[i][j] == approx_result
