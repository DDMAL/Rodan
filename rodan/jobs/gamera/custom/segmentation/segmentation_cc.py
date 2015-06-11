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


class Segmentation(RodanTask):
    name = "gamera.segmentation.segmentation_cc"
    author = "Yihong Luo & Rivu Khoda"
    description = "Finds staves using Miyao StaffFinder and Roach-Tatem StaffFinder and masks everything else using connected components"
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
        # loads the resource image using Gamera (this will be the image on which a mask will be applied at the end)
        original_image = load_image(inputs['input'][0]['resource_path'])

        # ROACH-TATEM SECTION

        # creates a staff_finder object 
        staff_finder = musicstaves.MusicStaves_rl_roach_tatem(original_image, 0, 0)
        # finds the staves with number of lines set to 4 
        staff_finder.remove_staves(u'all', 4)
        # returns the list of all vertices on each lines of each staff in the image 
        poly_list = staff_finder.get_staffpos()
        # contains the list of coordinates representing the corners of staff region 
        staff_regions = []

        for poly in poly_list:
            points = poly.staffrect   
            lt = (points.offset_x, points.offset_y)
            rt = (points.offset_x + points.ncols, points.offset_y)
            lb = (points.offset_x, points.offset_y + points.nrows)
            rb = (points.offset_x + points.ncols, points.offset_y + points.nrows)
            staff_regions.append([lt, rt, lb, rb]) #returns a list of tuples (coordinates)

        # pops the border of the image that is not a staff 
        staff_regions.pop()
        # loads the resource image using PIL
        resource_image = Image.open(inputs['input'][0]['resource_path'])
        # creates an image drawer object from the resource image 
        image_drawer = ImageDraw.Draw(resource_image)

        # reassigns ordering of polygon points so that a proper rectangle is drawn, and
        # increments or decrements coordinate value by 10 to expand the white margin to be drawn 
        # around the staff regions to disconnect larger neumes and lyrics 
        # (EFFECT: changing the x,y value will either increase or decrease the area of cc)

        for polygon in staff_regions:

            top_y = min(polygon[0][1], polygon[1][1])
            bottom_y = max(polygon[2][1], polygon[3][1])
            
            coordinates = [
                (polygon[0][0] - 3, top_y - 50),
                (polygon[1][0] + 3, top_y - 50),
                (polygon[1][0] + 3, bottom_y + 50),
                (polygon[0][0] - 3, bottom_y + 50)]

            image_drawer.polygon(coordinates, outline='white', fill=None)
        del image_drawer

        # converts to onebit image
        onebit_img = from_pil(resource_image).to_onebit()
        # obtains the ccs objects 
        ccs_temp = onebit_img.cc_analysis()
        # stores all ccs after the split
        ccs = []

        # split each cc horizontally
        for cc in ccs_temp:
            splitted = cc.splity([0.5])
            for split in splitted:
                ccs.append(split)

        # contains the coordinates representing the rectangles bounding the ccs objects 
        cc_regions = []

        # computes the cooridnates for a cc_region and appends it to the cc_regions list 
        for index in range(0, len(ccs)):
            lt = (ccs[index].offset_x, ccs[index].offset_y)
            rt = (ccs[index].offset_x + ccs[index].ncols, ccs[index].offset_y)
            lb = (ccs[index].offset_x, ccs[index].offset_y + ccs[index].nrows)
            rb = (ccs[index].offset_x + ccs[index].ncols, ccs[index].offset_y + ccs[index].nrows)
            cc_regions.append([lt, rt, lb, rb]) #returns a list of tuples

        # contains the list of cc that will be masked based on chosen set of constraints below     
        valid_images = [] 

         # for each corner cooridnates of a cc, add it list of valid images if it falls within in region occupied by the staff 
        for staff in staff_regions:
            for index, cc in enumerate(cc_regions):
                for corner in cc:
                    if staff[0][0] - 2 <= corner[0] <= staff[1][0] + 2 and staff[0][1] - 10 <= corner[1] <= staff[2][1] + 10:
                        # (EFFECT: Removes some of the large ornaments and letters)
                        if staff[0][1] - cc[0][1] < 51 and cc[2][1] - staff[2][1] < 51:
                            valid_images.append(ccs[index])
                            break

        # combines all cc images that satisfied the established restriction in line 49
        combined_images = image_utilities.union_images([image for image in valid_images])
        # creates a blank image of same size as the original_image RGB resource image
        blank_image = Image.new('L', (original_image.ncols, original_image.nrows), color='white')
        # creates an instance of Draw object to draw on the blank image 
        mask_drawer = ImageDraw.Draw(blank_image)

        # draws the a black masking polygon according to the points defining the staff region
        for polygon in staff_regions:
            # reassigns ordering of polygon points so that a proper rectangle is drawn
            reassign = [polygon[0], polygon[1], polygon[3], polygon[2]]
            cooridnates = [(coordinate[0], coordinate[1]) for coordinate in reassign]
            mask_drawer.polygon(cooridnates, outline='black', fill='black')
        del mask_drawer

        # converts the blank image which has black polygones drawn on it to format accetable by gamera
        mask_img = from_pil(blank_image).to_onebit()
        # combines the blank image with black polygones and CC images 
        segment_mask_roach = image_utilities.union_images([combined_images, mask_img])


        #################################################################################################
        #################################################################################################
        #################################################################################################

        # MIYAO SECTION

        # creates a staff_finder object 
        staff_finder = musicstaves.StaffFinder_miyao(original_image, 0, 0)
        # finds the staves with the default settings
        staff_finder.find_staves(0, 20, 0.8, -1)
        # returns the list of all vertices on each lines of each staff in the image 
        poly_list = staff_finder.get_polygon()
        # contains the list of coordinates representing the corners of staff region 
        staff_regions = []

        for index in range(0,len(poly_list)):
            top_row = poly_list[index][0]
            lt =  top_row.vertices[0]
            rt = top_row.vertices[len(top_row.vertices) - 1]
            bottom_row = poly_list[index][len(poly_list[index]) - 1]
            lb = bottom_row.vertices[0]
            rb = bottom_row.vertices[len(bottom_row.vertices) - 1]
            staff_regions.append([lt, rt, lb, rb]) #returns a list of point objects

        resource_image = Image.open(inputs['input'][0]['resource_path'])
        image_drawer = ImageDraw.Draw(resource_image)

        # reassigns ordering of polygon points so that a proper rectangle is drawn, and
        # increments or decrements coordinate value by 10 to expand the white margin to be drawn 
        # around the staff regions to disconnect larger neumes and lyrics 
        # (EFFECT: changing the x,y value will either increase or decrease the area of cc)

        for polygon in staff_regions:

            top_y = min(polygon[0].y, polygon[1].y)
            bottom_y = max(polygon[2].y, polygon[3].y)

            coordinates = [
                (polygon[0].x - 0, top_y - 50),
                (polygon[1].x + 0, top_y - 50),
                (polygon[1].x + 0, bottom_y + 50),
                (polygon[0].x - 0, bottom_y + 50)]

            image_drawer.polygon(coordinates, outline='white', fill=None)
        del image_drawer

        # converts to onebit image
        onebit_img = from_pil(resource_image).to_onebit()
        # obtains the ccs objects 
        ccs = onebit_img.cc_analysis()
        # contains the coordinates representing the rectangles bounding the ccs objects 
        cc_regions = []

        # computes the cooridnates for a cc_region and appends it to the cc_regions list 
        for index in range(0, len(ccs)):
            lt = (ccs[index].offset_x, ccs[index].offset_y)
            rt = (ccs[index].offset_x + ccs[index].ncols, ccs[index].offset_y)
            lb = (ccs[index].offset_x, ccs[index].offset_y + ccs[index].nrows)
            rb = (ccs[index].offset_x + ccs[index].ncols, ccs[index].offset_y + ccs[index].nrows)
            cc_regions.append([lt, rt, lb, rb]) #returns a list of tuples

        # contains the list of cc that will be masked based on chosen set of constraints below     
        valid_images = [] 

         # for each corner cooridnates of a cc, add it list of valid images if it falls within in region occupied by the staff 
        for staff in staff_regions:
            for index, cc in enumerate(cc_regions):
                for corner in cc:
                    if staff[0].x - 10 <= corner[0] <= staff[1].x + 10 and staff[0].y - 10 <= corner[1] <= staff[2].y + 10:
                        #(EFFECT: Removes some of the large ornaments and letters)
                        if staff[0].y - cc[0][1] < 51 and cc[2][1] - staff[2].y < 51:
                            valid_images.append(ccs[index])
                            break

        # combines all cc images that satisfied the established restriction in line 49
        combined_images = image_utilities.union_images([image for image in valid_images])
        # creates a blank image of same size as the original_image RGB resource image
        blank_image = Image.new('L', (original_image.ncols, original_image.nrows), color='white')
        # creates an instance of Draw object to draw on the blank image 
        mask_drawer = ImageDraw.Draw(blank_image)

        # draws the a black polygon according to the points defining the staff region
        for polygon in staff_regions:
            # reassigns ordering of polygon points so that a proper rectangle is drawn
            reassign = [polygon[0], polygon[1], polygon[3], polygon[2]]
            cooridnates = [(coordinate.x, coordinate.y) for coordinate in reassign]
            mask_drawer.polygon(cooridnates, outline='black', fill='black')
        del mask_drawer

        mask_img = from_pil(blank_image).to_onebit()
        # combines the blank image with black polygones and CC images 
        segment_mask_miyao = image_utilities.union_images([combined_images, mask_img])
        # combines the miyao mask and roach-tatem mask with logical 'or' tool 
        segment_mask = segment_mask_miyao.or_image(segment_mask_roach, False)
        # masks the original_image RGB resource image with the mask
        result_image_rgb = original_image.mask(segment_mask)
        # ensures the pixel type 
        result_image = ensure_pixel_type(result_image_rgb, outputs['output'][0]['resource_type'])
        # saves the image to specified path 
        result_image.save_PNG(outputs['output'][0]['resource_path'])












