# -----------------------------------------------------------------------------
# Program Name:         calvo_trainer.py
# Program Description:  Rodan wrapper for Calvo's classifier training
# -----------------------------------------------------------------------------

import cv2
import numpy as np
import os

from rodan.jobs.base import RodanTask
from . import training_engine as training

"""Wrap Calvo classifier training in Rodan."""


class CalvoTrainer(RodanTask):
    name = "Training model for Pixelwise Analysis of Music Document"
    author = "Jorge Calvo-Zaragoza, Gabriel Vigliensoni, and Ichiro Fujinaga"
    description = "The job performs the training of a neural network model for the pixelwise analysis of music document images."
    enabled = True
    category = "OMR - Layout analysis"
    interactive = False

    settings = {
        'title': 'Training parameters',
        'job_queue': 'GPU',
        'type': 'object',
        'properties': {
            'Maximum number of samples per class': {
                'type': 'integer',
                'minimum': 1,
                'default': 50
            },
            'Maximum number of training epochs': {
                'type': 'integer',
                'minimum': 1,
                'default': 5
            },
            'Vertical span': {
                'type': 'integer',
                'minimum': 1,
                'default': 25
            },
            'Horizontal span': {
                'type': 'integer',
                'minimum': 1,
                'default': 25
            }
        }
    }

    input_port_types = (
        {'name': 'Image', 'minimum': 1, 'maximum': 1, 'resource_types': lambda mime: mime.startswith('image/')},
        {'name': 'rgba PNG - Background layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Music symbol layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Staff lines layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Text', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'rgba PNG - Selected regions', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']}
    )

    output_port_types = (
        {'name': 'Model', 'minimum': 1, 'maximum': 1, 'resource_types': ['keras/model+hdf5']},
    )


    """
    How it works:
        - Layers are processed to create a categorical ground-truth:
            - Matrix with the same shape as the original input
            - Each cell contains a single categorical value
            - When no information is known about a pixel, it is indicated as -1 
        - Input and categorical images are used to call the training engine
            - The output port is also passed in order to ensure the availability of the destination
        - The training engine returns saves the model (+'.hdf5'), and return status
        - Because of how Rodan works, the path is renamed to the exact output port (-'.hdf5')
    """
    def run_my_task(self, inputs, settings, outputs):
        # Ports
        input_image = cv2.imread(inputs['Image'][0]['resource_path'], True) # 3-channel
        background = cv2.imread(inputs['rgba PNG - Background layer'][0]['resource_path'], cv2.IMREAD_UNCHANGED) # 4-channel
        notes = cv2.imread(inputs['rgba PNG - Music symbol layer'][0]['resource_path'], cv2.IMREAD_UNCHANGED) # 4-channel
        lines = cv2.imread(inputs['rgba PNG - Staff lines layer'][0]['resource_path'], cv2.IMREAD_UNCHANGED) # 4-channel
        text = cv2.imread(inputs['rgba PNG - Text'][0]['resource_path'], cv2.IMREAD_UNCHANGED) # 4-channel
        regions = cv2.imread(inputs['rgba PNG - Selected regions'][0]['resource_path'], cv2.IMREAD_UNCHANGED) # 4-channel

        # Settings
        vspan = settings['Vertical span']
        hspan = settings['Horizontal span']
        max_samples_per_class = settings['Maximum number of samples per class']
        max_number_of_epochs = settings['Maximum number of training epochs']

        # Create categorical ground-truth
        regions_mask = (regions[:, :, 3] == 255)

        notes_mask = (notes[:, :, 3] == 255)
        notes_mask = np.logical_and(notes_mask, regions_mask) # restrict layer to only the notes in the selected regions

        lines_mask = (lines[:, :, 3] == 255)
        lines_mask = np.logical_and(lines_mask, regions_mask) # restrict layer to only the staff lines in the selected regions

        text_mask = (text[:, :, 3] == 255)
        text_mask = np.logical_and(text_mask, regions_mask) # restrict layer to only the text in the selected regions

        background_mask = (background[:, :, 3] == 255) # background is already restricted to the selected regions (based on Pixel.js' behaviour)

        gt = np.ones((background.shape[0],background.shape[1]), 'uint8')*-1
        gt += (background_mask*1 + notes_mask*2 + lines_mask*3 + text_mask*4) # -> -1 or 0,1,2,3
        '''
        labeled = background_mask + notes_mask + lines_mask + text_mask
        
        for row in range(gt.shape[0]):
            for col in range(gt.shape[1]):
                if labeled[row][col]:
                    # Single category per pixel is assumed
                    gt[row][col] = (background_mask[row][col]*0
                                    + notes_mask[row][col]*1
                                    + lines_mask[row][col]*2
                                    + text_mask[row][col]*3)
        '''

        output_model_path = outputs['Model'][0]['resource_path']

        status = training.train_model(input_image,gt,
                                      hspan,vspan,
                                      output_model_path=output_model_path + '.hdf5',
                                      max_samples_per_class=max_samples_per_class,
                                      epochs=max_number_of_epochs)

        print('Finishing the job')
        os.rename(output_model_path + '.hdf5', output_model_path)

        return True
