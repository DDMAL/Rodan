import os
from functools import wraps

import PIL.Image
import PIL.ImageFile
import gamera.core
from vipsCC.VImage import VImage
from gamera.gameracore import Point
from gamera.toolkits.musicstaves.stafffinder import StafflinePolygon
from pymei import XmlExport
from djcelery_transactions import task
from django.conf import settings
from django.db import models

from rodan.models.results import Result
from rodan.models import Page
from rtask import RTask, RTaskMultiPage


Job = models.get_model('rodan', 'job')

other_input_mapping = {
    'segmented_image': lambda page: page.get_job_path(Job.objects.get(pk='segmentation'), 'tiff'),
    'page_sequence': lambda page: page.sequence,
    'project_id': lambda page: page.project.id,
}


def create_dirs(full_path):
    try:
        os.makedirs(os.path.dirname(full_path))
    except OSError:
        pass


def create_thumbnail(image_path, thumb_path, thumbnail_size):
    image = PIL.Image.open(image_path).convert('RGB')
    width, height = image.size

    if thumbnail_size != settings.ORIGINAL_SIZE:
        dimensions = (thumbnail_size, int(width / float(thumbnail_size) * height))
        image.thumbnail(dimensions, PIL.Image.ANTIALIAS)

    image.save(thumb_path)

    # Return the image dimensions so they can be used later
    return width, height


def create_thumbnails(image_path, result):
    page = result.page
    job = result.job_item.job

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        thumb_path = page.get_thumb_path(size=thumbnail_size, job=job)
        width, height = create_thumbnail(image_path, thumb_path, thumbnail_size)

    page.latest_width = width
    page.latest_height = height
    page.save()


def rodan_multi_page_task(inputs, others=[]):
    def inner_function(f):
        @task(base=RTaskMultiPage)
        @wraps(f)
        def real_inner(result_ids, **kwargs):
            input_types = (inputs,) if isinstance(inputs, str) else inputs

            #storing as tuples to avoid extra db lookups
            results_pages = [(Result.objects.get(pk=result_id), Page.objects.get(result=result_id)) for result_id in result_ids]

            # storing pages in seperate ds for sorting independently of the order in results_pages
            target_pages = [result_page[1] for result_page in results_pages]

            # always sort pages based on sequence no matter the input
            target_pages.sort(key=lambda page: page.sequence)

            input_paths_matrix = map(lambda input_type: [str(page.get_latest_file_path(input_type)) for page in target_pages], input_types)
            other_inputs_matrix = map(lambda other_type: [other_input_mapping[other_type](page) for page in target_pages], others)

            args = input_paths_matrix + other_inputs_matrix

            outputs = f(*args, **kwargs)

            # Loop through all the outputs and write them to disk
            for output_type, output_content in outputs.iteritems():
                for result_page in results_pages:
                    result = result_page[0]
                    page = result_page[1]

                    output_path = page.get_job_path(result.job_item.job, output_type)

                    create_dirs(output_path)

                    # Change the extension
                    if output_type == 'mei':
                        XmlExport.meiDocumentToFile(output_content, output_path.encode('ascii', 'ignore'))
                    else:
                        fp = open(output_path, 'w')
                        fp.write(output_content)
                        fp.close()

                    result.create_file(output_path, output_type)

            #update parameters and end times of all results and start next auto jobs
            for result_page in results_pages:
                result = result_page[0]
                page = result_page[1]
                result.update_end_total_time()
                result.save_parameters(**kwargs)
                page.start_next_automatic_job(result.user)

        return real_inner

    return inner_function


def rodan_task(inputs, others=[]):
    def inner_function(f):
        @task(base=RTask)
        @wraps(f)
        def real_inner(result_id, **kwargs):
            input_types = (inputs,) if isinstance(inputs, str) else inputs
            result = Result.objects.get(pk=result_id)
            page = result.page

            # Figure out the paths to the requested input files
            # For one input, pass in a string; for multiple, a tuple
            input_paths = map(page.get_latest_file_path, input_types)

            other_inputs = [other_input_mapping[other](page) for other in others]

            args = input_paths + other_inputs

            outputs = f(*args, **kwargs)

            # Loop through all the outputs and write them to disk
            for output_type, output_content in outputs.iteritems():
                output_path = page.get_job_path(result.job_item.job, output_type)

                create_dirs(output_path)

                # Change the extension
                if output_type == 'tiff':
                    # Write it with gamera (it's an image)
                    if isinstance(output_content, gamera.core.Image) or isinstance(output_content, gamera.core.SubImage):
                        gamera.core.save_image(output_content, output_path)
                    elif isinstance(output_content, PIL.Image.Image):
                        output_content.save(output_path)
                    else:
                        print "The output_content was not recognized.\n"

                    # Create thumbnails for the image as well
                    create_thumbnails(output_path, result)
                elif output_type == 'vips':
                    image_filepath, compression, tile_size = output_content
                    # All pyramidal tiff images must be saved in the same dir
                    vips_output = page.get_pyramidal_tiff_path()

                    # Used for debugging only (should really be done after project creation)
                    print "creating directories"
                    create_dirs(vips_output)

                    # Needs to be converted to a string (can't handle unicode)
                    image = VImage(str(image_filepath))
                    image.vips2tiff("{0}:{1},tile:{2}x{2},pyramid".format(vips_output, compression, tile_size))
                elif output_type == 'mei':
                    XmlExport.meiDocumentToFile(output_content.md, output_path.encode('ascii', 'ignore'))
                elif output_type == 'xml':
                    output_content.write_filename(output_path)
                else:
                    fp = open(output_path, 'w')
                    fp.write(output_content)
                    fp.close()

                result.create_file(output_path, output_type)

            # Mark the job as finished, and save the parameters
            result.update_end_total_time()
            result.save_parameters(**kwargs)

            # If the next job is automatic, start that too!
            page.start_next_automatic_job(result.user)

        return real_inner

    return inner_function


def load_image_for_job(path_to_image, job_gamera_func):
    '''
        load_image_for_job does two things:
            1) Loads the image using gamera's load_image function
            2) Converts the image to the appropriate pixel type needed as input by the gamera function supplied
                Note: The conversion will only occur if the input image is of wrong pixel type for the function and there are input
                types to the function other than ONEBIT. That is, if the only input type to the gamera function is
                ONEBIT, the input image will be returned without any conversion applied to it, even if its of wrong pixel type.
                The reason being we want to enforce conversion to ONEBIT only by applying a binarisation function to the image.

    '''
    loaded_img = gamera.core.load_image(path_to_image)

    return __convert_image_for_job(loaded_img, job_gamera_func.self_type.pixel_types)


def __convert_image_for_job(image, job_input_types):
    '''
    REFERENCE (based on gamera types):
        ONEBIT:     0
        GREYSCALE:  1
        GREY16:     2
        RGB:        3
        FLOAT:      4
        COMPLEX:    5
    '''
    image_type = image.data.pixel_type
    for job_type in job_input_types:
        if image_type == job_type:  # if the image type is present inside the list of job input type, return the image
            return image

    #if we get this far, need image conversion
    converted_img = None
    if 1 in job_input_types:  # prioritize GreyScale conversion if available
        converted_img = image.to_greyscale()
    elif 2 in job_input_types:  # then Grey16
        converted_img = image.to_grey16()
    elif 3 in job_input_types:  # then RGB
        converted_img = image.to_rgb()
    elif 4 in job_input_types:  # then Float
        converted_img = image.to_float()
    elif 5 in job_input_types:  # then COMPLEX
        converted_img = image.to_complex()
    else:  # else OneBit is only input option to job
        #Note that we return the original image, that is because we shouldn't convert directly to onebit
        return image

    return converted_img


def create_polygon_outer_points_json_dict(poly_list):
    '''
        The following function is used to retrieve polygon points data of the first
        and last staff lines of a particular polygon that is drawn over a staff.
        Note that we iterate through the points of the last staff line in reverse (i.e starting
        from the last point on the last staff line going to the first) - We do this to simplify
        recreating the polygon on the front-end
    '''
    poly_json_list = []

    for poly in poly_list:
        if len(poly):
            last_index = len(poly) - 1
            point_list_one = [(vert.x, vert.y) for vert in poly[0].vertices]
            point_list_last = [(vert.x, vert.y) for vert in poly[last_index].vertices]
            point_list_last.reverse()
            point_list_one.extend(point_list_last)
            poly_json_list.append(point_list_one)

    return poly_json_list


def create_json_from_poly_list(poly_list):
    poly_json_list = []

    for poly in poly_list:
        staff_list = []
        for staff in poly:
            point_list = [(vert.x, vert.y) for vert in staff.vertices]
            staff_list.append(point_list)
        poly_json_list.append(staff_list)

    return poly_json_list


def create_poly_list_from_json(encoded_poly_list):
    #print encoded_poly_list
    poly_list = []
    for poly in encoded_poly_list:
        staff_list = []
        for staff in poly:
            staffLine = StafflinePolygon()
            vertices = []
            for vert in staff:
                vertices.append(Point(vert[0], vert[1]))

            staffLine.vertices = vertices
            staff_list.append(staffLine)

        poly_list.append(staff_list)

    return poly_list


def fix_poly_point_list(poly_list, staffspace_height):
    for poly in poly_list:
        # Check if there are the same number of points on all staff lines
        lengths = [len(line.vertices) for line in poly]
        if len(set(lengths)) == 1:
            continue
        else:
            # Loop over all the staff lines
            for j, line in enumerate(poly):
                # Loop over all the points of the staff
                for k, vert in enumerate(line.vertices):
                    # Loop over all the staff lines again
                    for l, innerline in enumerate(poly):
                        if l == j:
                            # Prevent looping through the same line as outer
                            continue

                        if k < len(innerline.vertices):
                            # Make sure k is in range first
                            y_pix_diff = vert.x - innerline.vertices[k].x
                        else:
                            # It's not in range - we're missing a point
                            # Set this to an arbitrary value to force an insert
                            y_pix_diff = -10000

                        if -3 < y_pix_diff < 3:
                            # If the y-coordinate pixel difference is small enough
                            continue
                        else:
                            # Missing a point on that staff
                            # The multiplier represents the # of lines apart
                            staffspace_multiplier = l - j
                            new_y = vert.y + (staffspace_multiplier * staffspace_height)
                            innerline.vertices.insert(k, Point(vert.x, new_y))

    return poly_list
