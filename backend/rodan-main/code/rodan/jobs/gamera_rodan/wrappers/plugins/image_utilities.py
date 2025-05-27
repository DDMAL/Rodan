#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/plugins/image_utilities.py
# Purpose:                Wrapper for image utilities plugins.
#
# Copyright (C) 2016 DDMAL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

try:
    import gamera
    from gamera.core import load_image
    from gamera.plugins import image_utilities
except ImportError:
    pass
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class gamera_invert(RodanTask):

    name = 'Invert'
    author = 'Ryan Bannon'
    description = "Invert the image"
    settings ={'job_queue': 'Python3'}

    enabled = True
    category = 'Gamera - Image Utilities'
    interactive = False

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['PNG image'][0]['resource_path'])
        image_source.invert()
        for i in range(len(outputs['PNG image'])):
            image_source.save_PNG(outputs['PNG image'][i]['resource_path'])
        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_rgb_png_path = "/code/Rodan/rodan/test/files/lenna.png"
        input_onebit_png_path =  "/code/Rodan/rodan/test/files/lenna_one-bit-png_output.png"
        input_greyscale_png_path = "/code/Rodan/rodan/test/files/lenna_greyscale-png_output.png"
        input_grey16_png_path = "/code/Rodan/rodan/test/files/lenna_greyscale-16-png_output.png"

        output_rgb_png_path = testcase.new_available_path()
        output_onebit_png_path = testcase.new_available_path()
        output_greyscale_png_path = testcase.new_available_path()
        output_grey16_png_path = testcase.new_available_path()

        gt_rgb_png_path = "/code/Rodan/rodan/test/files/lenna_invert_lenna_output.png"
        gt_onebit_png_path = "/code/Rodan/rodan/test/files/lenna_invert_one-bit-png_output.png"
        gt_greyscale_png_path = "/code/Rodan/rodan/test/files/lenna_invert_greyscale-png_output.png"
        gt_grey16_png_path = "/code/Rodan/rodan/test/files/lenna_invert_greyscale-16-png_output.png"

        for input_path, out_path, gt_path in zip([input_rgb_png_path, input_onebit_png_path, input_greyscale_png_path, input_grey16_png_path],
                                                    [output_rgb_png_path, output_onebit_png_path, output_greyscale_png_path, output_grey16_png_path],
                                                    [gt_rgb_png_path, gt_onebit_png_path, gt_greyscale_png_path, gt_grey16_png_path]):
            inputs = {
                "PNG image": [{"resource_path":input_path}]
            }
            outputs = {
                "PNG image": [{"resource_path":out_path}]
            }
            self.run_my_task(inputs=inputs, outputs=outputs, settings={})

            # The predicted result and gt result should be identical to each other
            # The gt result is from running this job (niblack threshold) on production
            gt_output = cv2.imread(gt_path, cv2.IMREAD_UNCHANGED)
            pred_output = cv2.imread(out_path, cv2.IMREAD_UNCHANGED)

            np.testing.assert_array_equal(gt_output, pred_output, "Failed: {}".format(input_path))