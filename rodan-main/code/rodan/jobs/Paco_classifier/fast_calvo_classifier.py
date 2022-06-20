#-----------------------------------------------------------------------------
# Program Name:         calvo_classifier.py
# Program Description:  Rodan wrapper for Calvo's classifier
#-----------------------------------------------------------------------------

# Core
# import json
import os
import sys
import logging
import collections

# Third-party
import cv2
import numpy as np
from celery.utils.log import get_task_logger
from django.conf import settings as rodan_settings

# Project
from rodan.celery import app
from rodan.jobs.base import RodanTask
from rodan.models import Input

"""Wrap Fast Calvo classifier in Rodan."""

logger = get_task_logger(__name__)
# logger = get_task_logger('rodan')

class FastCalvoClassifier(RodanTask):
    name = "Fast Pixelwise Analysis of Music Document, Classifying"
    author = "Jorge Calvo-Zaragoza, Gabriel Vigliensoni, and Ichiro Fujinaga"
    description = "Given a pre-trained Convolutional neural network, the job performs a (fast) pixelwise analysis of music document images." 
    enabled = True
    category = "OMR - Layout analysis"
    interactive = False

    settings = {
        'title': 'Parameters',
        'type': 'object',
        'job_queue': 'GPU',
        'properties': {
            'Height': {
                'type': 'integer',
                'minimum': 1,
                'default': 256
            },
            'Width': {
                'type': 'integer',
                'minimum': 1,
                'default': 256
            },
            'Threshold': {
                'type': 'integer',
                'minimum': 0,
                'maximum': 100,
                'default': 50
            }
        },
    }

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 100, 'resource_types': lambda mime: mime.startswith('image/')},
        {'name': 'Background model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        # We did not go this route because it would be more difficult for the user to track layers.
        # {'name': 'Adjustable models', 'minimum': 1, 'maximum': 10, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 0', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 1', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
    )
    output_port_types = (
        {'name': 'Log File', 'minimum': 0, 'maximum': 1, 'resource_types': ['text/plain']},
        {'name': 'Background', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'Layers', 'minimum': 1, 'maximum': 10, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 0', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 1', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
    )

    """
    Entry point
    """
    def run_my_task(self, inputs, settings, outputs):
        from Paco_classifier import recognition_engine as recognition

        oldouts = sys.stdout, sys.stderr
        if 'Log File' in outputs and len(outputs['Log File']) > 0:
            handler = logging.FileHandler(outputs['Log File'][0]['resource_path'])
            handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            )
            logger.addHandler(handler)
        try:
            # Settings
            height = settings['Height']
            width = settings['Width']
            threshold = settings['Threshold']
            rlevel = app.conf.CELERY_REDIRECT_STDOUTS_LEVEL
            app.log.redirect_stdouts_to_logger(logger, rlevel)

            # Inner configuration
            mode = 'logical'

            # Fail early if the number of ports doesn't match.
            input_ports = len([x for x in inputs if x[:5] == 'Model'])
            output_ports = len([x for x in outputs if x[:5] == 'Layer'])
            if input_ports != output_ports:
                raise Exception(
                    'The number of input layers "Model" does not match the number of'
                    ' output "Layer"'
                )

            # Ports
            background_model = inputs['Background model'][0]['resource_path']
            model_paths = [background_model]

            # Populate optional ports
            for i in range(input_ports):
                model_paths += [inputs['Model %d' % i][0]['resource_path']]

            # Simulate a switch statement, instead of a series of ifs
            switch = {
                0: 'Background',
                1: 'Layer 0',
                2: 'Layer 1',
                3: 'Layer 2',
                4: 'Layer 3',
                5: 'Layer 4',
                6: 'Layer 5',
                7: 'Layer 6',
                8: 'Layer 7',
                9: 'Layer 8',
                10: 'Layer 9',
            }

            # status = {
            #     "inputs": inputs,
            #     "outputs": outputs,
            #     "input_ports": input_ports,
            #     "output_ports": output_ports,
            #     "input_": [x for x in inputs if x[:5] == "Model"],
            #     "output_": [x for x in outputs if x[:5] == "Layer"],
            #     "len_model_paths": len(model_paths),
            #     "model_paths": model_paths,
            #     "ports": []
            # }

            # Image input is a list of images, you can classify a list of images and this iterates on each image.
            for idx, _ in enumerate(inputs['Image']):

                # Process
                image_filepath = inputs['Image'][idx]['resource_path']
                image = cv2.imread(image_filepath, 1)
                analyses = recognition.process_image_msae(image, model_paths, height, width, mode = mode)

                for id_label, _ in enumerate(model_paths):
                    if mode == 'masks':
                        mask = ((analyses[id_label] > (threshold / 100.0)) * 255).astype('uint8')
                    elif mode == 'logical':
                        label_range = np.array(id_label, dtype=np.uint8)
                        mask = cv2.inRange(analyses, label_range, label_range)
     
                    original_masked = cv2.bitwise_and(image, image, mask = mask)
                    original_masked[mask == 0] = (255, 255, 255)

                    # Alpha = 0 when background
                    alpha_channel = np.ones(mask.shape, dtype=mask.dtype) * 255
                    alpha_channel[mask == 0] = 0
                    b_channel, g_channel, r_channel = cv2.split(original_masked)
                    original_masked_alpha = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

                    # status["ports"].append(
                    #     {
                    #         "switch": switch[id_label],
                    #         "path": outputs[switch[id_label]][idx]['resource_path'],
                    #     }
                    # )
                    if switch[id_label] in outputs:
                        cv2.imwrite(outputs[switch[id_label]][idx]['resource_path']+'.png', original_masked_alpha)
                        os.rename(outputs[switch[id_label]][idx]['resource_path']+'.png', outputs[switch[id_label]][idx]['resource_path'])

            # raise Exception(json.dumps(status, indent=2))
            return True
        finally:
            sys.stdout, sys.stderr = oldouts

    def my_error_information(self, exc, traceback):
        pass
