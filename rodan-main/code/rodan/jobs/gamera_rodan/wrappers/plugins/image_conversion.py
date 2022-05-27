#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------------------------

import gamera
from gamera.core import load_image
from gamera.plugins import image_conversion
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class gamera_to_rgb(RodanTask):

    name = 'Convert to RGB PNG'
    author = 'Ryan Bannon'
    description = image_conversion.to_rgb.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={}

    enabled = True
    category = 'Gamera - Image Conversion'
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

        image_source = load_image(inputs['PNG image'][0]['resource_path'])
        image_result = image_source.to_rgb()
        image_result.save_PNG(outputs['RGB PNG image'][0]['resource_path'])
        for i in range(len(outputs['RGB PNG image'])):
            image_result.save_PNG(outputs['RGB PNG image'][i]['resource_path'])
        return True

class gamera_to_greyscale(RodanTask):

    name = 'Convert to greyscale PNG'
    author = 'Ryan Bannon'
    description = image_conversion.to_greyscale.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={}

    enabled = True
    category = 'Gamera - Image Conversion'
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

        image_source = load_image(inputs['PNG image'][0]['resource_path'])
        image_result = image_source.to_greyscale()
        for i in range(len(outputs['Greyscale PNG image'])):
            image_result.save_PNG(outputs['Greyscale PNG image'][i]['resource_path'])
        return True

class gamera_to_grey16(RodanTask):

    name = 'Convert to greyscale 16 PNG'
    author = 'Ryan Bannon'
    description = image_conversion.to_grey16.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={}

    enabled = True
    category = 'Gamera - Image Conversion'
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
    author = 'Ryan Bannon'
    description = image_conversion.to_onebit.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={}

    enabled = True
    category = 'Gamera - Image Conversion'
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
