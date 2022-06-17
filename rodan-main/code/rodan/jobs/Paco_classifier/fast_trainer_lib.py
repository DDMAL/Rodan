"""Fast Trainer Library
This file provides the code for model generation.
Can be used in the standalone file or within Rodan.
"""

import logging
import os
import sys
import cv2
import numpy as np

try:
    import training_engine_sae as training
except Exception:
    import rodan.jobs.Paco_classifier.training_engine_sae as training


class CalvoTrainer:
    def __init__(
        self,
        batch_size,
        patch_height,
        patch_width,
        max_number_of_epochs,
        max_samples_per_class,
        file_selection_mode,
        sample_extraction_mode,
        inputs,
        outputs,
    ):
        self.batch_size = batch_size
        self.patch_height = patch_height
        self.patch_width = patch_width
        self.max_number_of_epochs = max_number_of_epochs
        self.max_samples_per_class = max_samples_per_class
        self.file_selection_mode = file_selection_mode
        self.sample_extraction_mode = sample_extraction_mode
        self.inputs = inputs
        self.outputs = outputs

        #file_selection_mode = training.FileSelectionMode.SHUFFLE
        #sample_extraction_mode = training.SampleExtractionMode.RANDOM

    def runTrainer(self):

        input_ports = len([x for x in self.inputs if "Layer" in x])
        output_ports = len([x for x in self.outputs if "Model" in x or "Log file" in x])
        if input_ports not in [output_ports, output_ports - 1]: # So it still works if Log File is added as an output. 
            raise Exception(
                'The number of input layers "rgba PNG - Layers" does not match the number of'
                ' output "Adjustable models"\n'
                "input_ports: " + str(input_ports) + " output_ports: " + str(output_ports)
            )

        # Create output models
        output_models_path = {}

        for i in range(input_ports):
            # ADDED .hdf5 to fix Rodan bug not recognizing output
            output_models_path[str(i)] = "{}.hdf5".format(self.outputs["Model " + str(i)][0]["resource_path"])
            # THIS IS NOT TAKING INTO ACCOUNT ANY FILE NOT NAMED MODEL IE BACKGROUND AND LOG!!!!

        # Call in training function
        status = training.train_msae( # TODO: Including patience parameter for early stopping
            inputs=self.inputs,
            num_labels=input_ports,
            height=self.patch_height,
            width=self.patch_width,
            output_path=output_models_path,
            file_selection_mode=self.file_selection_mode,
            sample_extraction_mode=self.sample_extraction_mode,
            epochs=self.max_number_of_epochs,
            number_samples_per_class=self.max_samples_per_class,
            batch_size=self.batch_size
        )
        print("Finishing the Fast CM trainer job.")
        for i in range(input_ports):
            os.rename(
                output_models_path[str(i)],
                self.outputs["Model " + str(i)][0]["resource_path"],
            )