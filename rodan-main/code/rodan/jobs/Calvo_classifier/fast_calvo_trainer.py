# -----------------------------------------------------------------------------
# Program Name:         calvo_trainer.py
# Program Description:  Rodan wrapper for Fast Calvo's classifier training
# -----------------------------------------------------------------------------

# Core
import logging
import sys

# Third-party
from celery.utils.log import get_task_logger

# Project
from rodan.celery import app
from rodan.jobs.base import RodanTask
from rodan.jobs.Calvo_classifier.fast_trainer_lib import CalvoTrainer

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
        "title": "Training parameters",
        "type": "object",
        "properties": {
            "Batch Size": {
                "type": "integer",
                "minimum": 1,
                "default": 16,
                "maximum": 64,
            },
            "Maximum number of training epochs": {
                "type": "integer",
                "minimum": 1,
                "default": 50,
            },
            "Maximum number of samples per label": {
                "type": "integer",
                "minimum": 100,
                "default": 2000,
            },
            "Patch height": {"type": "integer", "minimum": 32, "default": 256},
            "Patch width": {"type": "integer", "minimum": 32, "default": 256},
        },
        "job_queue": "GPU",
    }

    input_port_types = (
        {
            "name": "Image",
            "minimum": 1,
            "maximum": 5,
            "resource_types": ["image/rgb+png", "image/rgb+jpg"],
        },
        {
            "name": "rgba PNG - Selected regions",
            "minimum": 1,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'rgba PNG - Layers', 'minimum': 1, 'maximum': 10, 'resource_types': ['image/rgba+png']},
        {
            "name": "rgba PNG - Layer 0 (Background)",
            "minimum": 1,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 1",
            "minimum": 1,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 2",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 3",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 4",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 5",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 6",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 7",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 8",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "rgba PNG - Layer 9",
            "minimum": 0,
            "maximum": 5,
            "resource_types": ["image/rgba+png"],
        },
    )

    output_port_types = (
        # We did not go this route because it would be more difficult for the user to track layers
        # {'name': 'Adjustable models', 'minimum': 1, 'maximum': 10, 'resource_types': ['keras/model+hdf5']},
        {
            "name": "Log File",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["text/plain"],
        },
        {
            "name": "Model 0",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 1",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 2",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 3",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 4",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 5",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 6",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 7",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 8",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
        {
            "name": "Model 9",
            "minimum": 0,
            "maximum": 1,
            "resource_types": ["keras/model+hdf5"],
        },
    )

    def run_my_task(self, inputs, settings, outputs):
        oldouts = sys.stdout, sys.stderr
        if "Log File" in outputs:
            handler = logging.FileHandler(outputs["Log File"][0]["resource_path"])
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(message)s")
            )
            logger.addHandler(handler)
        try:
            # Settings
            batch_size = settings["Batch Size"]
            patch_height = settings["Patch height"]
            patch_width = settings["Patch width"]
            max_number_of_epochs = settings["Maximum number of training epochs"]
            max_samples_per_class = settings["Maximum number of samples per label"]

            rlevel = app.conf.CELERY_REDIRECT_STDOUTS_LEVEL
            app.log.redirect_stdouts_to_logger(logger, rlevel)

            # Fail if arbitrary layers are not equal before training occurs.
            trainer = CalvoTrainer(
                batch_size,
                patch_height,
                patch_width,
                max_number_of_epochs,
                max_samples_per_class,
                inputs,
                outputs,
            )
            trainer.runTrainer()
            return True
        finally:
            sys.stdout, sys.stderr = oldouts

    def my_error_information(self, exc, traceback):
        pass
