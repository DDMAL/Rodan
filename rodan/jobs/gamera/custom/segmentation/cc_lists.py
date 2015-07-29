from gamera.toolkits import musicstaves
from gamera.plugins import image_utilities
from PIL import Image
from PIL import ImageDraw
from gamera.plugins.pil_io import from_pil
from gamera.core import load_image

import sys


def get_margin(staff_finder, MARGIN_SIZE):
    '''Obtains the limit of how high or low a neume can be placed with respect to the upper and lower staff lines'''

    margin = staff_finder.staffspace_height * MARGIN_SIZE
    return margin


def get_pad(staff_finder, padx_factor, pady_factor):
    '''Obtains the pad_x and pad_y that are used in the process of selecting cc'''

    return (staff_finder.staffspace_height / padx_factor, staff_finder.staffspace_height / pady_factor)


def valid_border_region(element, borders):
    '''Checks if a connected componenet element or a staff falls within the defined boundaires of the pages'''
    left, right, top, bottom = borders

    if element[2][1] < bottom and element[0][1] > top and element[0][0] > left and element[1][0] < right:
        return True
    else:
        return False


def get_staff_regions(staff_finder, borders, DEBUG=False):
    '''
    Obtains a list containing information about positions of the staff and their lines,
    which in turn is used to compute the cc_vertices coordiantes of the polygons delimiting the staff regions
    '''

    # contains the list of coordinates representing the cc_verticess of staff region
    staff_regions = []

    if staff_finder.__class__.__name__ == "MusicStaves_rl_roach_tatem":
        poly_list = staff_finder.get_staffpos()

        for poly in poly_list:
            points = poly.staffrect
            lt = (points.offset_x, points.offset_y)
            rt = (points.offset_x + points.ncols, points.offset_y)
            lb = (points.offset_x, points.offset_y + points.nrows)
            rb = (points.offset_x + points.ncols, points.offset_y + points.nrows)
            staff = [lt, rt, lb, rb]

            # Check if the staff is in the valid region
            if valid_border_region(staff, borders):
                staff_regions.append(staff)  # Returns list of tuples (coordinates)
    else:
        poly_list = staff_finder.get_polygon()

        for index in range(0, len(poly_list)):
            top_row = poly_list[index][0]
            lt = (top_row.vertices[0].x, top_row.vertices[0].y)
            rt = (top_row.vertices[len(top_row.vertices) - 1].x, top_row.vertices[len(top_row.vertices) - 1].y)
            bottom_row = poly_list[index][len(poly_list[index]) - 1]
            lb = (bottom_row.vertices[0].x, bottom_row.vertices[0].y)
            rb = (bottom_row.vertices[len(bottom_row.vertices) - 1].x, bottom_row.vertices[len(bottom_row.vertices) - 1].y)
            staff = [lt, rt, lb, rb]

            # Check if the staff is in the valid region
            if valid_border_region(staff, borders):
                staff_regions.append(staff)  # Returns a list of tuples (coordinates)

    # =========DEBUG MODE==================================
    if DEBUG:
        if len(staff_regions) == 0:
            quit("staff detection failed")

    # ========================================================

    return staff_regions


def draw_whitebox(salz_image, staff_regions, margin, RESULT_PATH=None, name=None, DEBUG=False):
    """
    draws white lines above and below the staff with using specified margins

    reassigns ordering of polygon points so that a proper rectangle is drawn, and
    increments or decrements coordinate value by 10 to expand the white margin to be drawn
    around the staff regions to disconnect larger neumes and lyrics
    (EFFECT: changing the x,y value will either increase or decrease the area of cc)
    """

    image_drawer = ImageDraw.Draw(salz_image)

    for polygon in staff_regions:

        coordinates = [
            (polygon[0][0], polygon[0][1] - margin),
            (polygon[1][0], polygon[0][1] - margin),
            (polygon[1][0], polygon[3][1] + margin),
            (polygon[0][0], polygon[3][1] + margin)]

        image_drawer.polygon(coordinates, outline='white', fill=None)
    del image_drawer

    # =========DEBUG MODE==================================
    if DEBUG:
        salz_image.save(RESULT_PATH + "/" + "white_line_" + name, "png")

    #  ========================================================

    return salz_image


def cc_analysis(salz_image):
    '''Applies connected component anaylsis on an image'''

    # converts to onebit image
    onebit_img = from_pil(salz_image).to_onebit()
    # obtains the ccs objects
    cc_list = onebit_img.cc_analysis()
    return cc_list


def split(cc_list):
    '''Split each cc horizontally'''

    cc_split_list = []

    for cc in cc_list:
        splitted = cc.splity([0.5])
        for split in splitted:
            cc_split_list.append(split)

    return cc_split_list


def cc_coordinates(cc_list):
    '''Computes the cooridnates for a cc_region and appends it to the cc_regions list'''

    cc_regions = []

    for index in range(0, len(cc_list)):
        lt = (cc_list[index].offset_x, cc_list[index].offset_y)
        rt = (cc_list[index].offset_x + cc_list[index].ncols, cc_list[index].offset_y)
        lb = (cc_list[index].offset_x, cc_list[index].offset_y + cc_list[index].nrows)
        rb = (cc_list[index].offset_x + cc_list[index].ncols, cc_list[index].offset_y + cc_list[index].nrows)
        cc = [lt, rt, lb, rb]
        cc_regions.append(cc)

    return cc_regions


def is_in_staff(staff, vertices, pad_x, pad_y):
    '''Checks if a connected component falls within the boundaries of a staff'''
    for vertex in vertices:
        if staff[0][0] - pad_x <= vertex[0] <= staff[1][0] + pad_x and staff[0][1] - pad_y <= vertex[1] <= staff[2][1] + pad_y:
            return True
    return False


def small_enough(staff, cc, margin):
    '''Checks if a connected component is larger than conventional neume size '''

    if staff[0][1] - cc[0][1] < margin and cc[2][1] - staff[2][1] < margin:
        return True
    else:
        return False


def combine(valid_images, staff_regions, salz_image, RESULT_PATH=None, name=None,  DEBUG=False):
    '''
    Combines all connected component images into a single image, then draws a mask on each staff region
    on a new blank image, which are in turn combined together.
    '''

    combined_images = image_utilities.union_images([image for image in valid_images])

    # ===========DEBUG MODE=================================================================

    if DEBUG:
        combined_images.save_image(RESULT_PATH + "/" + "combined_images_" + name)

    # ===================================================================================

    # Creates a blank image of same size as the original_image RGB resource image
    blank_image = Image.new('L', (salz_image.ncols, salz_image.nrows), color='white')
    # Creates an instance of Draw object to draw on the blank image
    mask_drawer = ImageDraw.Draw(blank_image)
    # Draws the black masking polygon according to the points defining the staff region
    for staff in staff_regions:
        # Reassigns ordering of polygon points so that a proper rectangle is drawn
        reassign = [staff[0], staff[1], staff[3], staff[2]]
        coordinates = [(coordinate[0], coordinate[1]) for coordinate in reassign]
        mask_drawer.polygon(coordinates, outline='black', fill='black')
    del mask_drawer

    # ============DEBUG MODE===================================

    if DEBUG:
        blank_image.save(RESULT_PATH + "/" + "blank_image_" + name, "png")

    # =========================================================

    mask_img = from_pil(blank_image).to_onebit()
    # combines the blank image with black polygones and CC images
    segment_mask_single = image_utilities.union_images([combined_images, mask_img])

    return segment_mask_single
