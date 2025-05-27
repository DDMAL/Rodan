#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/classification.py
# Purpose:                Wrapper for classification.
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
    import gamera.core
    import gamera.gamera_xml
    import gamera.classify
    import gamera.knn
    from gamera.plugins import segmentation
except ImportError:
    pass

from rodan.jobs.base import RodanTask


class CCAnalysis(RodanTask):
    name = 'CC Analysis'
    author = "Andrew Fogarty"
    description = """
    Performs connected component analysis on the image.

    This algorithm assumes 8-connected components, meaning any two
    pixels are considered "connected" if they are adjacent in any
    direction, including diagonally.

    The original image will have all of its pixels "labeled" with a
    number representing each connected component.  This is so the
    connected components can share data with their source image and
    makes things much more efficient.

    Returns a list of ccs found in the image.  Since all the CC's
    share the same data with the original image, changing the CC's
    will affect the original.  If you do not want this behavior, use
    the image_copy_ function on each of the CCs::

      ccs = [x.image_copy() for x in ccs]

    .. _image_copy: utility.html#image-copy
    """
    enabled = True
    category = "Gamera - Classification"
    interactive = False
    settings = {'job_queue': 'Python3'}
    input_port_types = [{
        'name': '1-Bit PNG Image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'GameraXML - Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        image_path = inputs['1-Bit PNG Image'][0]['resource_path']
        input_image = gamera.core.load_image(image_path)
        ccs = input_image.cc_analysis()
        output_xml = gamera.gamera_xml.WriteXMLFile(glyphs=ccs,
                                                    with_features=True)
        output_xml.write_filename(
            outputs['GameraXML - Connected Components'][0]['resource_path'])

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_despeckle_png_path = "/code/Rodan/rodan/test/files/240r_despeckle_output.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/240r_CC-analysis_output.xml"
        inputs = {
            "1-Bit PNG Image": [{"resource_path":input_despeckle_png_path}]
        }
        outputs = {
            "GameraXML - Connected Components": [{"resource_path":output_path}]
        }
        settings = {
        }

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))
        # also each line should be identical to its counterpart
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))