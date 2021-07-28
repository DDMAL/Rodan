#!/usr/bin/env python
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

import gamera.core
import gamera.gamera_xml
import gamera.classify
import gamera.knn
from gamera.plugins import segmentation
from rodan.jobs.base import RodanTask


class CCAnalysis(RodanTask):
    name = 'CC Analysis'
    author = "Andrew Fogarty"
    description = segmentation.cc_analysis.escape_docstring().replace("\\n", "\n").replace( '\\"', '"')
    enabled = True
    category = "Gamera - Classification"
    interactive = False
    settings = {}
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
