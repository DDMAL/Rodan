import os
from functools import wraps

import PIL.Image
import PIL.ImageFile
import gamera.core
from gamera.gameracore import Point
from celery.task import task
from django.conf import settings

from rodan.models.results import Result
from rodan.models.projects import JobItem


def create_dirs(full_path):
    try:
        os.makedirs(os.path.dirname(full_path))
    except OSError:
        pass


def create_thumbnails(output_path, result):
    page = result.page
    job = result.job_item.job
    image = PIL.Image.open(output_path)
    width, height = image.size

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        dimensions = (thumbnail_size, int(width / float(thumbnail_size) * height))
        image.thumbnail(dimensions, PIL.Image.ANTIALIAS)
        image.save(page.get_thumb_path(size=thumbnail_size, job=job))
        # Have to open a new image for the next iteration of the loop
        image = PIL.Image.open(output_path)


def rodan_task(inputs=''):
    def inner_function(f):
        @task
        @wraps(f)
        def real_inner(result_id, **kwargs):
            input_types = (inputs,) if isinstance(inputs, str) else inputs
            result = Result.objects.get(pk=result_id)
            page = result.page

            # Figure out the paths to the requested input files
            # For one input, pass in a string; for multiple, a tuple
            input_paths = map(page.get_latest_file_path, input_types)

            outputs = f(*input_paths, **kwargs)

            # Loop through all the outputs and write them to disk
            for output_type, output_content in outputs.iteritems():
                output_path = page.get_job_path(result.job_item.job, output_type)

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
                    create_thumbnails(output_path, result)
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

            # If the next job is automatic, start that too!
            next_job = page.get_next_job()
            next_job_obj = next_job.get_object()
            if next_job_obj.is_automatic:
                job_item = JobItem.objects.get(workflow=page.workflow, job=next_job)
                next_result = Result.objects.create(job_item=job_item, page=page, user=result.user)
                next_result.update_end_manual_time()
                next_job_obj.on_post(next_result.id, **next_job_obj.parameters)

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
        last_index = len(poly) - 1
        point_list_one = [(vert.x, vert.y) for vert in poly[0].vertices]
        point_list_last = [(vert.x, vert.y) for vert in poly[last_index].vertices]
        point_list_last.reverse()
        point_list_one.extend(point_list_last)
        poly_json_list.append(point_list_one)

    return poly_json_list


def fix_poly_point_list(poly_list, staffspace_height):
    for poly in poly_list:
        # Check if there are the same number of points on all staff lines
        lengths = [len(line.vertices) for line in poly]
        if len(set(lengths)) == 1:
            continue
        else:
            # Loop over all the staff lines
            for j in xrange(0,len(poly)):#loop over all 4 staff lines
                for k in xrange(0,len(poly[j].vertices)):#loop over points of staff
                    for l in xrange(0,len(poly)):#loop over all 4 staff lines
                        if l == j:# optimization to not loop through the same staff line as outer loop
                            continue

                        if(k < len(poly[l].vertices)): #before doing the difference make sure index k is within indexable range of poly[l]
                            y_pix_diff = poly[j].vertices[k].x - poly[l].vertices[k].x
                        else:
                            #if it's not in range, we are missing a point since, the insertion grows the list as we go through the points
                            y_pix_diff = -10000 #arbitrary value to evaluate next condition to false and force an insert
                            
                        if(y_pix_diff < 3 and y_pix_diff > -3): #if the y coordinate pixel difference within acceptable deviation
                            continue
                        else:
                            #missing a point on that staff
                            staffspace_multiplier = (l - j) #represents the number of staff lines apart from one another
                            poly[l].vertices.insert(k, Point(poly[j].vertices[k].x, poly[j].vertices[k].y + (staffspace_multiplier * staffspace_height)))

    return poly_list
