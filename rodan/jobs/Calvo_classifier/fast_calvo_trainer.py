# -----------------------------------------------------------------------------
# Program Name:         calvo_trainer.py
# Program Description:  Rodan wrapper for Fast Calvo's classifier training
# -----------------------------------------------------------------------------

# Core
import logging
import os
import sys

# Third-party
from celery.utils.log import get_task_logger
import cv2
import numpy as np

# Project
from rodan.celery import app
from rodan.jobs.base import RodanTask
from . import training_engine_sae as training

"""Wrap Patchwise (Fast) Calvo classifier training in Rodan."""

logger = get_task_logger(__name__)


class FastCalvoTrainer(RodanTask):
    name = "Training model for Patchwise Analysis of Music Document"
    author = "Jorge Calvo-Zaragoza, Francisco J. Castellanos, Gabriel Vigliensoni, and Ichiro Fujinaga"
    description = "The job performs the training of many Selection Auto-Encoder model for the pixelwise analysis of music document images."
    enabled = True
    category = "OMR - Layout analysis"
    interactive = False

    settings = {
        'title': 'Training parameters',
        'type': 'object',
        'properties': {
            'Batch Size': {
                'type': 'integer',
                'minimum': 1,
                'default': 16,
                'maximum': 64,
            },
            'Maximum number of training epochs': {
                'type': 'integer',
                'minimum': 1,
                'default': 50
            },
            'Maximum number of samples per label': {
                'type': 'integer',
                'minimum': 100,
                'default': 2000
            },            
            'Patch height': {
                'type': 'integer',
                'minimum': 32,
                'default': 256
            },
            'Patch width': {
                'type': 'integer',
                'minimum': 32,
                'default': 256
            },
        },
        'job_queue': 'GPU'
    }

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 5, 'resource_types': ['image/rgb+png','image/rgb+jpg']},
        {'name': 'rgba PNG - Selected regions', 'minimum': 1, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'rgba PNG - Layers', 'minimum': 1, 'maximum': 10, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 0 (Background)', 'minimum': 1, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 1', 'minimum': 1, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 2', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 3', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 4', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 5', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 6', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 7', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 8', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Layer 9', 'minimum': 0, 'maximum': 5, 'resource_types': ['image/rgba+png']},
    )

    output_port_types = (
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'Adjustable models', 'minimum': 1, 'maximum': 10, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Log File', 'minimum': 1, 'maximum': 1, 'resource_types': ['text/plain']},
        {'name': 'Model 0', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 1', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
        {'name': 'Model 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['keras/model+hdf5']}
    )


    def run_my_task(self, inputs, settings, outputs):
        oldouts = sys.stdout, sys.stderr
        if 'Log File' in outputs:
            handler = logging.FileHandler(outputs['Log File'][0]['resource_path'])
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            )
            logger.addHandler(handler)
        try:
            # Settings
            batch_size = settings['Batch Size']
            patch_height = settings['Patch height']
            patch_width = settings['Patch width']
            max_number_of_epochs = settings['Maximum number of training epochs']
            max_samples_per_class = settings['Maximum number of samples per label']

            rlevel = app.conf.CELERY_REDIRECT_STDOUTS_LEVEL
            app.log.redirect_stdouts_to_logger(logger, rlevel)

            # Fail if arbitrary layers are not equal before training occurs.
            input_ports = len([x for x in inputs if "Layer" in x]) 
            output_ports = len([x for x in outputs if "Model" in x or "Log file" in x])
            if input_ports not in [output_ports, output_ports - 1]: # So it still works if Log File is added as an output. 
                raise Exception(
                    'The number of input layers "rgba PNG - Layers" does not match the number of'
                    ' output "Adjustable models"\n'
                    "input_ports: " + str(input_ports) + " output_ports: " + str(output_ports)
                )

            # Required input ports
            # TODO assert that all layers have the same number of inputs (otherwise it will crack afterwards)
            number_of_training_pages = len(inputs["Image"])

            input_images = []
            gts = []

            # Create output models
            output_models_path = {}

            for idx in range(number_of_training_pages):
                input_image = cv2.imread(inputs["Image"][idx]["resource_path"], cv2.IMREAD_COLOR)  # 3-channel
                background = cv2.imread(
                    inputs["rgba PNG - Layer 0 (Background)"][idx]["resource_path"],
                    cv2.IMREAD_UNCHANGED,
                )  # 4-channel
                regions = cv2.imread(
                    inputs["rgba PNG - Selected regions"][idx]["resource_path"],
                    cv2.IMREAD_UNCHANGED,
                )  # 4-channel

                # Create categorical ground-truth
                gt = {}
                TRANSPARENCY = 3
                regions_mask = regions[:, :, TRANSPARENCY] == 255
                # background is already restricted to the selected regions (based on Pixel.js' behaviour)

                # Populate remaining inputs and outputs
                bg_mask = background[:, :, TRANSPARENCY] == 255
                gt["0"] = np.logical_and(bg_mask, regions_mask)

                for i in range(1, input_ports):
                    file_obj = cv2.imread(
                        inputs["rgba PNG - Layer {layer_num}".format(layer_num=i)][idx]["resource_path"],
                        cv2.IMREAD_UNCHANGED,
                    )
                    file_mask = file_obj[:, :, TRANSPARENCY] == 255
                    gt[str(i)] = np.logical_and(file_mask, regions_mask)

                input_images.append(input_image)
                gts.append(gt)

            for i in range(input_ports):
                output_models_path[str(i)] = outputs["Model " + str(i)][0]["resource_path"] + ".hdf5"
                
            # Call in training function
            status = training.train_msae(
                input_images=input_images,
                gts=gts,
                num_labels=input_ports,
                height=patch_height,
                width=patch_width,
                output_path=output_models_path,
                epochs=max_number_of_epochs,
                max_samples_per_class=max_samples_per_class,
                batch_size=batch_size,
            )

            print("Finishing the Fast CM trainer job.")
            for i in range(input_ports):
                os.rename(output_models_path[str(i)], outputs["Model " + str(i)][0]["resource_path"])
            return True
        finally:
            sys.stdout, sys.stderr = oldouts

    def my_error_information(self, exc, traceback):
        pass