#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamera functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/plugins/morphology.py
# Purpose:                Wrapper for morphology plugins.
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
# --------------------------------------------------------------------------------------------------

try:
    import gamera
    from gamera.core import load_image
    from gamera.plugins import morphology
except ImportError:
    pass
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')


class gamera_despeckle(RodanTask):

    name = 'Despeckle'
    author = 'Ryan Bannon'
    description = """
  Removes connected components that are smaller than the given size.

  *size*
    The maximum number of pixels in each connected component that
    will be removed.

  This approach to finding connected components uses a pseudo-recursive
  descent, which gets around the hard limit of ~64k connected components
  per page in ``cc_analysis``.  Unfortunately, this approach is much
  slower as the connected components get large, so *size* should be
  kept relatively small.

  *size* == 1 is a special case and runs much faster, since it does not
  require recursion.
  """
    settings = {
        'title': 'Despeckle settings',
        'type': 'object',
        'job_queue': 'Python3',
        'properties': {
            'Connected component size': {
                'type': 'integer',
                'default': 1,
                'minimum': 1,
                'description': 'iThe maximum number of pixels in each connected component that will be removed. 1 is a special case that runs faster as it does not require recursion.'
            }
        }
    }

    enabled = True
    category = "Gamera - Morphology"
    interactive = False

    input_port_types = [{
        'name': 'Onebit PNG image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Onebit PNG despeckled image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_result = load_image(inputs['Onebit PNG image'][0]['resource_path'])
        image_result.despeckle(settings['Connected component size']) 
        for i in range(len(outputs['Onebit PNG despeckled image'])):
            image_result.save_PNG(outputs['Onebit PNG despeckled image'][i]['resource_path'])
        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_onebit_png_path = "/code/Rodan/rodan/test/files/240r_onebit-png_output.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/240r_despeckle_output.png"
        inputs = {
            "Onebit PNG image": [{"resource_path":input_onebit_png_path}]
        }
        outputs = {
            "Onebit PNG despeckled image": [{"resource_path":output_path}]
        }
        settings = {
            'Connected component size': 1
        }

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The predicted result and gt result should be identical to each other
        # The gt result is from running this job (niblack threshold) on production
        gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
        pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        np.testing.assert_array_equal(gt_output, pred_output)


class gamera_dilate(RodanTask):

    name = 'Dilate'
    author = 'Gabriel Vigliensoni'
    description =   """
  Morpholgically dilates the image with a 3x3 square structuring element.

  The returned image is of the same size as the input image, which means
  that border pixels are not dilated beyond the image dimensions. If you
  also want the border pixels to be dilated, apply pad_image_ to the input
  image beforehand.

.. _pad_image: utility.html#pad-image
  """
    settings = {'title': 'Despeckle settings',
                'type': 'object',
                'job_queue': 'Python3'
                }

    enabled = True
    category = "Gamera - Morphology"
    interactive = False

    input_port_types = [{
        'name': 'Onebit PNG image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Onebit PNG dilated image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]


    def run_my_task(self, inputs, settings, outputs):

        image_result = load_image(inputs['Onebit PNG image'][0]['resource_path'])
        processed_image = image_result.dilate()
        for i in range(len(outputs['Onebit PNG dilated image'])):
            processed_image.save_PNG(outputs['Onebit PNG dilated image'][i]['resource_path'])
        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_onebit_png_path = "/code/Rodan/rodan/test/files/lenna_one-bit-png_output.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/lenna_dilate_output.png"
        inputs = {
            "Onebit PNG image": [{"resource_path":input_onebit_png_path}]
        }
        outputs = {
            "Onebit PNG dilated image": [{"resource_path":output_path}]
        }
        settings = {
            'Connected component size': 1
        }

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The predicted result and gt result should be identical to each other
        # The gt result is from running this job (niblack threshold) on production
        gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
        pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        np.testing.assert_array_equal(gt_output, pred_output)