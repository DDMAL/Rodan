#!/usr/bin/env python
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
