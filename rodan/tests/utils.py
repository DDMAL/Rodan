import os

from django.utils import unittest
from django.conf import settings

import gamera.core
import gamera.toolkits.musicstaves

import rodan.jobs.utils
import rodan.jobs.staff_finding


class TestPolyListSerialization(unittest.TestCase):
    def setUp(self):
        default_params = rodan.jobs.staff_finding.StaffFinding.parameters

        self.staff_finder = gamera.toolkits.musicstaves.StaffFinder_miyao(\
            gamera.core.load_image(os.path.join(settings.PROJECT_DIR, "tests/test_resources/testimg.tiff")), 0, 0)
        self.staff_finder.find_staves(default_params["num_lines"],\
            default_params['scanlines'], default_params['blackness'],\
            default_params['tolerance'])
        self.orig_poly_list = self.staff_finder.get_polygon()

    def runTest(self):
        self.json_poly_list = \
            rodan.jobs.utils.create_json_from_poly_list(self.orig_poly_list)

        self.new_poly_list = \
            rodan.jobs.utils.create_poly_list_from_json(self.json_poly_list)

        self.assertEqual(len(self.orig_poly_list), len(self.new_poly_list))
        for i, poly in enumerate(self.orig_poly_list):
            self.assertEqual(len(poly), len(self.new_poly_list[i]))
            for j, staff in enumerate(poly):
                self.assertEqual(len(staff.vertices), len(self.new_poly_list[i][j].vertices))
                for k, point in enumerate(staff.vertices):
                    self.assertEqual(point.x, self.new_poly_list[i][j].vertices[k].x)
                    self.assertEqual(point.y, self.new_poly_list[i][j].vertices[k].y)
