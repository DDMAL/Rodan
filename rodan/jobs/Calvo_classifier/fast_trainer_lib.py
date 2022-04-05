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
    import rodan.jobs.Calvo_classifier.training_engine_sae as training


class CalvoTrainer:
    def __init__(
        self,
        batch_size,
        patch_height,
        patch_width,
        max_number_of_epochs,
        max_samples_per_class,
        inputs,
        outputs,
    ):
        self.batch_size = batch_size
        self.patch_height = patch_height
        self.patch_width = patch_width
        self.max_number_of_epochs = max_number_of_epochs
        self.max_samples_per_class = max_samples_per_class
        self.inputs = inputs
        self.outputs = outputs

    def runTrainer(self):

        input_ports = len([x for x in self.inputs if "Layer" in x])
        output_ports = len([x for x in self.outputs if "Model" in x or "Log file" in x])
        if input_ports not in [
            output_ports,
            output_ports - 1,
        ]:  # So it still works if Log File is added as an output.
            raise Exception(
                'The number of input layers "rgba PNG - Layers" does not match the number of'
                ' output "Adjustable models"\n'
                "input_ports: "
                + str(input_ports)
                + " output_ports: "
                + str(output_ports)
            )

        # Required input ports
        # TODO assert that all layers have the same number of inputs (otherwise it will crack afterwards)
        number_of_training_pages = len(self.inputs["Image"])

        input_images = []
        gts = []

        # Create output models
        output_models_path = {}

        for idx in range(number_of_training_pages):
            input_image = cv2.imread(
                self.inputs["Image"][idx]["resource_path"], cv2.IMREAD_COLOR
            )  # 3-channel
            background = cv2.imread(
                self.inputs["rgba PNG - Layer 0 (Background)"][idx]["resource_path"],
                cv2.IMREAD_UNCHANGED,
            )  # 4-channel
            regions = cv2.imread(
                self.inputs["rgba PNG - Selected regions"][idx]["resource_path"],
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
                    self.inputs["rgba PNG - Layer {layer_num}".format(layer_num=i)][
                        idx
                    ]["resource_path"],
                    cv2.IMREAD_UNCHANGED,
                )
                file_mask = file_obj[:, :, TRANSPARENCY] == 255
                gt[str(i)] = np.logical_and(file_mask, regions_mask)

            input_images.append(input_image)
            gts.append(gt)

        for i in range(input_ports):
            output_models_path[str(i)] = self.outputs["Model " + str(i)][0][
                "resource_path"
            ]
            # THIS IS NOT TAKING INTO ACCOUNT ANY FILE NOT NAMED MODEL IE BACKGROUND AND LOG!!!!

        # Call in training function
        status = training.train_msae(
            input_images=input_images,
            gts=gts,
            num_labels=input_ports,
            height=self.patch_height,
            width=self.patch_width,
            output_path=output_models_path,
            epochs=self.max_number_of_epochs,
            max_samples_per_class=self.max_samples_per_class,
            batch_size=self.batch_size,
        )

        print("Finishing the Fast CM trainer job.")
        for i in range(input_ports):
            os.rename(
                output_models_path[str(i)],
                self.outputs["Model " + str(i)][0]["resource_path"],
            )
