from rodan.jobs.base import RodanTask
from .extract_c_clefs import *
import cv2 as cv
import os
import json
import logging

logger = logging.getLogger("rodan")


class ExtractCClefs(RodanTask):
    name = "Extract C Clefs"
    author = "Lucas March"
    description = "Finds the C clefs from a generated XML file from the interactive classifier and exports them to seperate images."
    enabled = True
    category = "Image Processing"
    interactive = False
    settings = {
        "title": "Settings",
        "type": "object",
        "job_queue": "Python3",
    }
    input_port_types = (
        {
            "name": "PNG Image",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["image/rgba+png"],
        },
        {
            "name": "XML file",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["application/gamera+xml"],
        },
    )
    output_port_types = (
        {
            "name": "C Clef",
            "minimum": 1,
            "maximum": 20,
            "is_list": True,
            "resource_types": ["image/rgba+png"],
        },
    )

    def run_my_task(self, inputs, settings, outputs):
        logger.info("Running C Clef Extraction")

        image_path = inputs["PNG Image"][0]["resource_path"]
        image_name = inputs["PNG Image"][0]["resource_name"]
        xml_path = inputs["XML file"][0]["resource_path"]

        image = load_image(image_path)
        xml = load_xml(xml_path)
        coords = extract_coords(xml)
        if not coords:
            raise Exception("No C Clefs found in XML File.")
        cropped_images = crop_images(image, coords)
        output_base_path = outputs["C Clef"][0]["resource_folder"]
        logger.info(f"output base path {output_base_path}")
        for i, cropped_image in enumerate(cropped_images):
            index = i + 1  # Start indexing from 1
            output_path = f"{output_base_path}{image_name}_{index}.png"
            save_image(cropped_image, output_path)

        return True
