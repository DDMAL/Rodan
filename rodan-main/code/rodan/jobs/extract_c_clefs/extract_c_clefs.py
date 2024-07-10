import argparse
import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional


def crop_images(
    image: np.ndarray, coords: List[Tuple[int, int, int, int]]
) -> List[np.ndarray]:
    """
    Crop the image based on the coordinates.
    Args:
        image (np.ndarray): The image to crop.
        coords (List[Tuple[int, int, int, int]]): List of tuples (ulx, uly, lrx, lry) for cropping.
    Returns:
        List[np.ndarray]: List of cropped image regions as numpy arrays.
    """
    crops = []
    for ulx, uly, lrx, lry in coords:
        crop = image[uly:lry, ulx:lrx]
        crops.append(crop)
    return crops


def save_image(image: np.ndarray, output_path: str) -> None:
    """
    Save the image to the specified path.
    Args:
        image (np.ndarray): The image to save.
        output_path (str): The path to save the image.
    """
    cv2.imwrite(output_path, image)
    print(f"Cropped image saved to {output_path}")


def load_image(path: str) -> np.ndarray:
    """
    Load an image from the specified path.
    Args:
        path (str): Path to the image file.
    Returns:
        np.ndarray: The loaded image.
    """
    return cv2.imread(path, cv2.IMREAD_COLOR)


def load_xml(path: str) -> ET.Element:
    """
    Load an XML file from the specified path.
    Args:
        path (str): Path to the XML file.
    Returns:
        ET.Element: The root element of the parsed XML.
    """
    tree = ET.parse(path)
    return tree.getroot()


def extract_coords(xml: ET.Element) -> List[Optional[Tuple[int, int, int, int]]]:
    """
    Extract bounding box coordinates from the XML element.
    Args:
        xml (ET.Element): The root element of the parsed XML.
    Returns:
        List[Optional[Tuple[int, int, int, int]]]: List of tuples (ulx, uly, lrx, lry) for cropping.
    """
    coords_list = []
    for glyph in xml.findall(".//glyph"):
        for id_tag in glyph.findall(".//id"):
            if id_tag.attrib["name"] == "clef.c":
                ulx = int(glyph.attrib["ulx"])
                uly = int(glyph.attrib["uly"])
                ncols = int(glyph.attrib["ncols"])
                nrows = int(glyph.attrib["nrows"])
                lrx = ulx + ncols
                lry = uly + nrows
                coords_list.append((ulx, uly, lrx, lry))
    return coords_list
