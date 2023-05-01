#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/masking.py
# Purpose:                Wrapper for simple masking operations.
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
    from gamera.core import Image, load_image
except ImportError:
    pass

from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class GameraMaskLogicalAnd(RodanTask):

    name = 'Mask (logical \'and\')'
    author = 'Ryan Bannon'
    description =   """
  Perform the AND operation on two images.

  Since it would be difficult to determine what exactly to do if the images
  are a different size, the two images must be the same size.

  *in_place*
    If true, the operation will be performed in-place, changing the
    contents of the current image.

  See or_image_ for some usage examples.
  """
    settings ={'job_queue': 'Python3'}
    enabled = True
    category = 'Gamera - Masking'
    interactive = False

    input_port_types = [{
        'name': 'Source image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    },
    {
        'name': 'Mask image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Source image with mask applied',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['Source image'][0]['resource_path'])
        image_mask = load_image(inputs['Mask image'][0]['resource_path'])
        image_result = image_source.and_image(image_mask)
        for i in range(len(outputs['Source image with mask applied'])):
            image_result.save_PNG(outputs['Source image with mask applied'][i]['resource_path'])
        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_onebit_png_path = "/code/Rodan/rodan/test/files/lenna_one-bit-png_output.png"
        input_mask_path = "/code/Rodan/rodan/test/files/lenna_mask.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/lenna_maskAnd_one-bit.png"
        inputs = {
            "Source image": [{"resource_path":input_onebit_png_path}],
            "Mask image": [{"resource_path":input_mask_path}]
        }
        outputs = {
            "Source image with mask applied": [{"resource_path":output_path}]
        }
        settings = {}

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The predicted result and gt result should be identical to each other
        # The gt result is from running this job on production
        gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
        pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        np.testing.assert_array_equal(gt_output, pred_output)

class GameraMaskLogicalXor(RodanTask):

    name = 'Mask (logical \'xor\')'
    author = 'Ryan Bannon'
    description =   """
  Perform the XOR operation on two images.

  Since it would be difficult to determine what exactly to do if the images
  are a different size, the two images must be the same size.

  *in_place*
    If true, the operation will be performed in-place, changing the
    contents of the current image.

  See or_image_ for some usage examples.
  """
    settings ={'job_queue': 'Python3'}
    enabled = True
    category = 'Gamera - Masking'
    interactive = False

    input_port_types = [{
        'name': 'Source image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    },
    {
        'name': 'Mask image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Source image with mask applied',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['Source image'][0]['resource_path'])
        image_mask = load_image(inputs['Mask image'][0]['resource_path'])
        image_result = image_source.xor_image(image_mask)
        for i in range(len(outputs['Source image with mask applied'])):
            image_result.save_PNG(outputs['Source image with mask applied'][i]['resource_path'])
        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_onebit_png_path = "/code/Rodan/rodan/test/files/lenna_one-bit-png_output.png"
        input_mask_path = "/code/Rodan/rodan/test/files/lenna_mask.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/lenna_maskXor_one-bit.png"
        inputs = {
            "Source image": [{"resource_path":input_onebit_png_path}],
            "Mask image": [{"resource_path":input_mask_path}]
        }
        outputs = {
            "Source image with mask applied": [{"resource_path":output_path}]
        }
        settings = {}

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # The predicted result and gt result should be identical to each other
        # The gt result is from running this job on production
        gt_output = cv2.imread(gt_output_path, cv2.IMREAD_UNCHANGED)
        pred_output = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        np.testing.assert_array_equal(gt_output, pred_output)