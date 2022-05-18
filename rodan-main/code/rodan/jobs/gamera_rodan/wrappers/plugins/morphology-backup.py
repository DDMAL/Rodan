#!/usr/bin/env python
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

from gamera.core import load_image
from gamera.plugins import morphology
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')


class gamera_despeckle(RodanTask):

    name = 'Despeckle'
    author = 'Ryan Bannon'
    description = morphology.despeckle.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {
        'title': 'Despeckle settings',
        'type': 'object',
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


class gamera_dilate(RodanTask):

    name = 'Dilate'
    author = 'Gabriel Vigliensoni'
    description = morphology.dilate.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {'title': 'Despeckle settings',
                'type': 'object'
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
