import os
from functools import wraps

import PIL.Image
import PIL.ImageFile
import gamera.core
from gamera.gameracore import Point
from celery.task import task

from rodan.models.results import Result


def create_dirs(full_path):
    try:
        os.makedirs(os.path.dirname(full_path))
    except OSError:
        pass


def create_thumbnails(output_path, result):
    page = result.page
    job = result.job_item.job
    image = PIL.Image.open(output_path)
    original_size = image.size
    small_width = 100
    large_width = 400
    small_size = (small_width, original_size[0] / float(small_width) * original_size[1])
    large_size = (large_width, original_size[0] / float(large_width) * original_size[1])

    image.thumbnail(small_size, PIL.Image.ANTIALIAS)
    image.save(page.get_path_to_image('small', job))

    image = PIL.Image.open(output_path)
    image.thumbnail(large_size, PIL.Image.ANTIALIAS)
    image.save(page.get_path_to_image('large', job))


def rodan_task(inputs=''):
    def inner_function(f):
        @task
        @wraps(f)
        def real_inner(result_id, **kwargs):
            input_types = (inputs,) if isinstance(inputs, str) else inputs
            result = Result.objects.get(pk=result_id)

            # Figure out the paths to the requested input files
            # For one input, pass in a string; for multiple, a tuple
            input_paths = map(result.page.get_latest_file, input_types)

            outputs = f(*input_paths, **kwargs)

            # Loop through all the outputs and write them to disk
            for output_type, output_content in outputs.iteritems():
                job_filepath = result.page.get_filename_for_job(result.job_item.job)
                output_path = "%s.%s" % (os.path.splitext(job_filepath)[0], output_type)

                create_dirs(output_path)

                # Change the extension
                if output_type == 'tiff':
                    # Write it with gamera (it's an image)
                    if isinstance(output_content, gamera.core.Image) or isinstance(output_content, gamera.core.SubImage):
                        gamera.core.save_image(output_content, output_path)
                    elif isinstance(output_content, PIL.ImageFile.ImageFile):
                        output_content.save(output_path)
                    else:
                        print "The output_content was not recognized.\n"

                    # Create thumbnails for the image as well
                    # create_thumbnails(output_path, result)
                elif output_type == 'mei':
                    # This is a special case because an object is used
                    pass
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
        point_list_one = [(vert.x, vert.y) for vert in poly[0].vertices]
        point_list_four = [(vert.x, vert.y) for vert in poly[3].vertices]
        point_list_four.reverse()
        point_list_one.extend(point_list_four)
        poly_json_list.append(point_list_one)

    return poly_json_list


def fix_poly_point_list(poly_list, staffspace_height):
    for poly in poly_list:
        #following condition checks if there are the same amount of points on all 4 staff lines
        if len(poly[0].vertices) == len(poly[1].vertices) and \
        len(poly[0].vertices) == len(poly[2].vertices) and \
        len(poly[0].vertices) == len(poly[3].vertices):
            continue
        else:
            for j, line in enumerate(poly):
                for k, vert in enumerate(line.vertices):
                    for m, innerline in enumerate(poly):
                        if line == innerline:
                            continue
                        if k < len(line.vertices):
                            y_pix_diff = vert.x - innerline.vertices[k].x
                        else:
                            y_pix_diff = -10000

                        if y_pix_diff < 3 and y_pix_diff > -3:
                            continue
                        else:
                            staffspace_multiplier = m - j
                            line.vertices.insert(k, Point(vert.x, vert.y + (staffspace_multiplier * staffspace_height)))

    return poly_list
