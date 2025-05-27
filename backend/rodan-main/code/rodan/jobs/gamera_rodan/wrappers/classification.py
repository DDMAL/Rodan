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

from ast import Import
import os
from shutil import copyfile
import logging
logger = logging.getLogger("rodan")
try:
    import gamera.core
    import gamera.gamera_xml
    import gamera.classify
    import gamera.knn
    from gamera.gamera_xml import glyphs_from_xml
except ImportError:
    pass

from rodan.jobs.base import RodanTask


class ClassificationTask(RodanTask):
    name = 'Non-Interactive Classifier'
    author = "Ling-Xiao Yang"
    description = "Performs classification on a binarized staff-less image and outputs an xml file."
    enabled = True
    category = "Gamera - Classification"
    settings = {
        'title': 'Bounding box size',
        'type': 'object',
        'job_queue': 'Python3',
        'properties': {
            'Bounding box size': {
                'type': 'integer',
                'minimum': 1,
                'default': 4
            }
        }
    }
    interactive = False

    input_port_types = [{
        'name': 'GameraXML - Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'GameraXML - Training Data',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'GameraXML - Feature Selection',
        'resource_types': ['application/gamera+xml'],
        'minimum': 0,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'GameraXML - Classified Glyphs',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 2
    }]

    def run_my_task(self, inputs, settings, outputs):
        classifier_path = inputs['GameraXML - Training Data'][0]['resource_path']
        with self.tempdir() as tdir:
            tempPath = os.path.join(tdir, classifier_path + '.xml')
        copyfile(classifier_path, tempPath)
        cknn = gamera.knn.kNNNonInteractive(tempPath)
        if 'GameraXML - Feature Selection' in inputs:
            cknn.load_settings(inputs['GameraXML - Feature Selection'][0]['resource_path'])
        func = gamera.classify.BoundingBoxGroupingFunction(
            settings['Bounding box size'])
        # Load the connected components
        logger.info("going to load the connected components")
        ccs = glyphs_from_xml(
            inputs['GameraXML - Connected Components'][0]['resource_path'])
        # Do grouping
        logger.info(("grouping funciton has type: {0}").format(type(func)))
        logger.info(("the ccs variable is: {0} and has type {1}").format(ccs, type(ccs)))
        cs_image = cknn.group_and_update_list_automatic(ccs,
                                                        grouping_function=func,
                                                        max_parts_per_group=4,
                                                        max_graph_size=16)
        # Generate the Gamera features
        cknn.generate_features_on_glyphs(cs_image)
        # Write the glyphs to GameraXML
        output_xml = gamera.gamera_xml.WriteXMLFile(glyphs=cs_image,
                                                    with_features=True)
        for i in range(len(outputs['GameraXML - Classified Glyphs'])):
            output_xml.write_filename(
                outputs['GameraXML - Classified Glyphs'][i]['resource_path'])

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_ccAnalysis = "/code/Rodan/rodan/test/files/238r-CCAnalysis.xml"
        input_feature_selection = "/code/Rodan/rodan/test/files/238r-GameraXML_feature_selection.xml"
        input_training_data = "/code/Rodan/rodan/test/files/238r-GameraXML_training_data.xml"

        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/238r-nic.xml"


        inputs = {
            "GameraXML - Connected Components": [{"resource_path":input_ccAnalysis}],
            "GameraXML - Training Data": [{"resource_path":input_training_data}],
            "GameraXML - Feature Selection": [{"resource_path":input_feature_selection}]
        }
        outputs = {
            "GameraXML - Classified Glyphs": [{"resource_path":output_path}]
        }
        settings = {
            "Bounding box size":4
        }

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # NIC includes randomness, so each time, the prediction will be slightly different
        # As a result we only make sure that the output file exists and is not empty
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertNotEqual(0, len(predicted))
        del predicted