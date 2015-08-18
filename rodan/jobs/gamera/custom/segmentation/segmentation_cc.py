from gamera.toolkits import musicstaves
from gamera.plugins import image_utilities
from PIL import Image
from PIL import ImageDraw
from gamera.plugins.pil_io import from_pil
from gamera.core import load_image
import json, jsonschema
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from gamera.toolkits.musicstaves import MusicStaves_rl_roach_tatem
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from rodan.jobs.gamera.custom.segmentation.cc_lists import *


class Segmentation(RodanTask):
    name = "gamera.segmentation.segmentation_cc"
    author = "Yihong Luo & Rivu Khoda"
    description = "Finds staves using Miyao StaffFinder and Roach-Tatem StaffFinder and masks everything else using connected components."
    settings = {}
    enabled = True
    category = "Segmentation"
    interactive = False

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png','image/greyscale+png','image/grey16+png','image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/onebit+png','image/greyscale+png','image/grey16+png','image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        # Max factor by which a neume can be outside of a staff
        MARGIN_SIZE = 1.5

        # Corresponds to the estimated borders of an input image
        borders = (300, 3900, 300, 5500)

        # To create roach staff finder object
        roach_staffline_height = 0
        roach_staffspace_height = 0

        # For is_in_staff method
        pad_factor_roach = (12, 6)
        pad_factor_miyao = (6, 6)

        # To create miyao staff finder object
        miyao_staffline_height = 0
        miyao_staffspace_height = 0

        # Miyao_settings = (num_lines, scan_lines, blackness, tolerance)
        miyao_settings = (0, 15, 0.8, -1)

        # -------------------------------------------------------------------------------

        original_image = load_image(inputs['input'][0]['resource_path'])

        # -------------------------------------------------------------------------------

        # Creates a staff_finder object
        staff_finder = musicstaves.MusicStaves_rl_roach_tatem(original_image, roach_staffline_height, roach_staffspace_height)
        # Finds the staves with number of lines set to 4
        staff_finder.remove_staves(u'all', 4)
        # Obtains the coordinates for the vertices of every staff in the image
        staff_regions = get_staff_regions(staff_finder, borders)
        # Opens another copy of image through PIL
        copy_image = Image.open(inputs['input'][0]['resource_path'])
        # Obtains the limit of how high or low a neume can be placed with respect to the staff lines
        MARGIN = get_margin(staff_finder, MARGIN_SIZE)
        # Draws a white line on top and bottom of staffs
        image_with_whitebox = draw_whitebox(copy_image, staff_regions, MARGIN)
        # Applies a connected component analysis on the image
        cc_list = cc_analysis(image_with_whitebox)
        # Splits the connected component images horizontally
        cc_split_list = split(cc_list)
        # Obtains the coordinates of verticies for all connected components
        cc_regions = cc_coordinates(cc_split_list)
        # Creates an empty list that will store valid images of cc based on set conditions
        valid_images = []
        # Gets the desired value of padding to be added to the staff region
        pad_x, pad_y = get_pad(staff_finder, *pad_factor_roach)

        for staff in staff_regions:
            for index, cc in enumerate(cc_regions):
                if is_in_staff(staff, cc, pad_x, pad_y):
                    if small_enough(staff, cc, MARGIN):
                        valid_images.append(cc_split_list[index])

        # Produces a masking image
        segment_mask_roach = combine(valid_images, staff_regions, original_image)

        # -------------------------------------------------------------------------------

        # Creates a staff_finder object
        staff_finder = musicstaves.StaffFinder_miyao(original_image, miyao_staffline_height, miyao_staffspace_height)
        # Finds the staves with the default settings
        staff_finder.find_staves(*miyao_settings)
        # Obtains the coordinates for the vertices of every staff in the image
        staff_regions = get_staff_regions(staff_finder, borders)
        # Opens another copy of image through PIL
        copy_image = Image.open(inputs['input'][0]['resource_path'])
        # Obtains the limit of how high or low a neume can be placed with respect to the staff lines
        MARGIN = get_margin(staff_finder, MARGIN_SIZE)
        # Draws a white line on top and bottom of staffs
        image_with_whitebox = draw_whitebox(copy_image, staff_regions, MARGIN)
        # Applies a connected component analysis on the image
        cc_list = cc_analysis(image_with_whitebox)
        cc_regions = cc_coordinates(cc_list)
        # Obtains the coordinates of verticies for all connected components
        valid_images = []
        # Gets the desired value of padding to be added to the staff region
        pad_x, pad_y = get_pad(staff_finder, *pad_factor_miyao)

        for staff in staff_regions:
            for index, cc in enumerate(cc_regions):
                if is_in_staff(staff, cc, pad_x, pad_y):
                    if small_enough(staff, cc, MARGIN):
                        valid_images.append(cc_list[index])

        # Produces a masking image
        segment_mask_miyao = combine(valid_images, staff_regions, original_image)
        # ------------------------------------------------------------------------------

        # Combines the miyao mask and roach-tatem mask with logical 'or' tool
        segment_mask = segment_mask_miyao.or_image(segment_mask_roach, False)
        # Masks the original_image RGB resource image with the mask
        result_image_rgb = original_image.mask(segment_mask)
        # ensures the pixel type
        result_image = ensure_pixel_type(result_image_rgb, outputs['output'][0]['resource_type'])
        # saves the image to specified path
        result_image.save_PNG(outputs['output'][0]['resource_path'])

