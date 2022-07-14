#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           gamera-rodan
# Program Description:    Job wrappers that allows some Gamrea functionality to work in Rodan.
#
# Filename:               gamera-rodan/wrappers/toolkits/document-preprocessing-toolkit/stable_paths.py
# Purpose:                Wrapper for stable paths detection.
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
from gamera.toolkits.stable_paths_toolkit.plugins import stable_path_staff_detection
from rodan.jobs.base import RodanTask

import logging
logger = logging.getLogger('rodan')

class StablePaths(RodanTask):

    name = 'Stable Paths - remove'
    author = 'Ryan Bannon'
    description = stable_path_staff_detection.removeStaves.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={'job_queue': 'Python3'}

    enabled = True
    category = 'Gamera - Document Preprocessing Toolkit'
    interactive = False

    input_port_types = [{
        'name': 'Onebit PNG image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'Onebit PNG image (staves removed)',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):

        image_source = load_image(inputs['Onebit PNG image'][0]['resource_path'])
        image_result = image_source.removeStaves()
        for i in range(len(outputs['Onebit PNG image (staves removed)'])):
            image_result.save_PNG(outputs['Onebit PNG image (staves removed)'][i]['resource_path'])
        return True

class StablePathDetection(RodanTask):

    name = 'Stable Paths - detection'
    author = 'Ryan Bannon'
    description = stable_path_staff_detection.stablePathDetection.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings ={
        'title': 'Stable Paths Detection',
        'type': 'object',
        'job_queue': 'Python3',
        'properties': {
            'Trimming': {
                'type': 'boolean',
                'default': True,
                'description': 'Trims staff sets where white space or ornamentations are found.'
            },
            'Deletion': {
                'type': 'boolean',
                'default': True,
                'description': 'If checked, the image will be processed once, keeping what it finds to be the staves and then the code is run again. More accurate for images with a lot of lyrics or ornamentation.'
            },
            'Staff fixing': {
                'type': 'boolean',
                'default': True,
                'description': 'Uses the slopes of staff sets to fix staff lines that differ wildly from the slope at specific intervals.'
            }
        }
    }

    enabled = True
    category = 'Gamera - Document Preprocessing Toolkit'
    interactive = False

    input_port_types = [{
        'name': 'Onebit PNG image',
        'resource_types': ['image/onebit+png'],
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

        image_source = load_image(inputs['Onebit PNG image'][0]['resource_path'])
        image_result = image_source.stablePathDetection(settings['Trimming'], settings['Deletion'], settings['Staff fixing'])
        for i in range(len(outputs['RGB PNG image'])):
            image_result.save_PNG(outputs['RGB PNG image'][i]['resource_path'])
        return True
