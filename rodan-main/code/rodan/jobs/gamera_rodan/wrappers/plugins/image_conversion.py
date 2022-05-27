#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/plugins/image_conversion.py
# Purpose:                Wrapper for image conversion plugins.
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

from rodan.jobs.base import RodanTask

import cv2
from PIL import Image
import numpy as np
import logging
from gamera.core import load_image
from gamera.plugins import image_conversion

logger = logging.getLogger('rodan')


class gamera_to_rgb(RodanTask):
    name = 'Convert to RGB PNG'
    author = 'Ryan Bannon - Shahrad Mohammadzadeh'
    description = \
        "Converts the given image to an RGB image according to the following rules: \
- for ONEBIT images, 0 is mapped to (255,255,255) and everything else to (0,0,0) \
- for GREYSCALE and GREY16 images, R=G=B \
- for FLOAT images, the range [min,max] is linearly mapped to the 256 grey values"
    settings = {}

    enabled = True
    category = 'Image Conversion'
    interactive = False

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'RGB PNG image',
        'resource_types': ['image/rgb+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):
        # use cv2 to read image and change to rgb png format.
        logging.info("The input path is:", inputs['PNG image'][0]['resource_path'])
        image_source = cv2.imread(inputs['PNG image'][0]['resource_path'])
        im_rgb = cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB)  # bgr to rgb

        logging.info("converted the picture and now trying to save using pillow.")
        logging.info("The output image numpy format is: ", np.array(im_rgb))
        for i in range(len(outputs['RGB PNG image'])):
            path = outputs['RGB PNG image'][i]['resource_path']
            logging.info("The file destination is: " + path)
            Image.fromarray(im_rgb).save(path, format="png")
        return True


class gamera_to_greyscale(RodanTask):
    name = 'Convert to greyscale PNG'
    author = 'Ryan Bannon - Shahrad Mohammadzadeh'
    description = \
        "Converts the given image to a GREYSCALE image according to the \
following rules: \
- for ONEBIT images, 0 is mapped to 255 and everything else to 0. \
- for FLOAT images, the range [min,max] is linearly scaled to [0,255] \
- for GREY16 images, the range [0,max] is linearly scaled to [0,255] \
- for RGB images, the luminance is used, which is defined in VIGRA as 0.3*R + 0.59*G + 0.11*B"
    settings = {}

    enabled = True
    category = 'Image Conversion'
    interactive = False

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Greyscale PNG image',
        'resource_types': ['image/greyscale+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):
        # use cv2 to read image and change to Greyscale 16 png format.
        logging.info("The input path is:", inputs['PNG image'][0]['resource_path'])
        image_source = cv2.imread(inputs['PNG image'][0]['resource_path'])
        gray = cv2.cvtColor(image_source, cv2.COLOR_BGR2GRAY)  # bgr to rgb

        logging.info("converted the picture and now trying to save using pillow.")
        logging.info("The output image numpy format is: ", np.array(gray))
        for i in range(len(outputs['Greyscale PNG image'])):
            path = outputs['Greyscale PNG image'][i]['resource_path']
            logging.info("The file destination is: " + path)
            Image.fromarray(gray).save(path, format="png")
        return True


class gamera_to_grey16(RodanTask):
    name = 'Convert to greyscale 16 PNG'
    author = 'Ryan Bannon - Shahrad Mohammadzadeh'
    description = \
        "Converts the given image to a GREY16 image according to the \
following rules: \
- for ONEBIT images, 0 is mapped to 65535 and everything else to 0. \
- for FLOAT images, the range [min,max] is linearly scaled to [0,65535] \
- for GREYSCALE images, pixel values are copied unchanged \
- for RGB images, the luminance is used, which is defined in VIGRA as 0.3*R + 0.59*G + 0.11*B. This results only in a value range [0,255]"
    settings = {}

    enabled = True
    category = 'Image Conversion'
    interactive = False

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Greyscale 16 PNG image',
        'resource_types': ['image/grey16+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['PNG image'][0]['resource_path'])
        image_result = image_source.to_grey16()
        for i in range(len(outputs['Greyscale 16 PNG image'])):
            image_result.save_PNG(outputs['Greyscale 16 PNG image'][i]['resource_path'])
        return True


class gamera_to_onebit(RodanTask):
    name = 'Convert to one-bit (black and white) PNG'
    author = 'Ryan Bannon - Shahrad Mohammadzadeh'
    description = \
        "Converts the given image to a ONEBIT image. First the image is converted \
    and then the otsu_threshold_ algorithm is applied. \
    For other ways to convert to ONEBIT images, see the Binarization_ category."

    settings = {}

    enabled = True
    category = 'Image Conversion'
    interactive = False

    input_port_types = [{
        'name': 'PNG image',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'One-bit PNG image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['PNG image'][0]['resource_path'])
        image_result = image_source.to_onebit()
        for i in range(len(outputs['One-bit PNG image'])):
            image_result.save_PNG(outputs['One-bit PNG image'][i]['resource_path'])
        return True
