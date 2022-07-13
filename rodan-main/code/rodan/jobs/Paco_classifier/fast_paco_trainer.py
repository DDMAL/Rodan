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
import zipfile
from shutil import rmtree

# Project
from rodan.celery import app
from rodan.jobs.base import RodanTask

"""Wrap Patchwise (Fast) Calvo classifier training in Rodan."""

logger = get_task_logger(__name__)


class FastPacoTrainer(RodanTask):
    name = "Training model for Patchwise Analysis of Music Document, Training"
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
                'default': 8,
                'maximum': 64,
            },
            'Maximum number of training epochs': {
                'type': 'integer',
                'minimum': 1,
                'default': 50
            },
            'Maximum number of samples per label': {
                'type': 'integer',
                'minimum': 1,
                'default': 1000
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
        {'name': 'Sample 1', 'minimum': 1, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 2', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'rgba PNG - Layers', 'minimum': 1, 'maximum': 10, 'resource_types': ['image/rgba+png']},
        {'name': 'Sample 3', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 10', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 11', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 12', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 13', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 14', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 15', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 16', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 17', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 18', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 19', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
        {'name': 'Sample 20', 'minimum': 0, 'maximum': 1, 'resource_types': ['application/zip']},
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
        from Paco_classifier import training_engine_sae as training
        from Paco_classifier.fast_trainer_lib import PacoTrainer
        from Paco_classifier import input_settings_test

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
            number_samples_per_class = settings['Maximum number of samples per label']

            #------------------------------------------------------------
            #TODO Include the training options in the configuration data
            file_selection_mode = training.FileSelectionMode.SHUFFLE 
            sample_extraction_mode = training.SampleExtractionMode.RANDOM
            #------------------------------------------------------------

            # Unzip zip files into dictionary of images
            if os.path.exists('unzipping_folder'):
                rmtree('unzipping_folder')
            os.mkdir('unzipping_folder')
            new_input = {}
            create_folder = True
            folder_num = 1
            for ipt in inputs:
                dir_path = 'unzipping_folder/{}'.format(folder_num)
                folder_num += 1
                with zipfile.ZipFile(inputs[ipt][0]['resource_path'], 'r') as zip_ref:
                    zip_ref.extractall(dir_path)
                full_path = os.path.join(os.getcwd(), dir_path)
                for f in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, f)):
                        layer_name = f.split(".")[0]
                        if create_folder:
                            new_input[layer_name] = []
                        new_input[layer_name].append({'resource_path': os.path.join(full_path, f)})
                create_folder = False

            # SANITY CHECK
            # logger.info(new_input)
            input_settings_test.pre_training_check(new_input, batch_size, patch_height, patch_width, number_samples_per_class)

            rlevel = app.conf.CELERY_REDIRECT_STDOUTS_LEVEL
            app.log.redirect_stdouts_to_logger(logger, rlevel)

            # Fail if arbitrary layers are not equal before training occurs.
            trainer = PacoTrainer(
                batch_size,
                patch_height,
                patch_width,
                max_number_of_epochs,
                number_samples_per_class,
                file_selection_mode,
                sample_extraction_mode,
                # CHANGED HERE FOR UNZIP
                new_input,
                outputs,
            )
            trainer.runTrainer()

            # REMOVE UNZIP FOLDER
            if os.path.exists('unzipping_folder'):
                rmtree('unzipping_folder')

            return True
        finally:
            sys.stdout, sys.stderr = oldouts

    def my_error_information(self, exc, traceback):
        pass
