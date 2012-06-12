import os

import gamera.core


def create_result_output_dirs(full_output_path):
    output_dir = os.path.dirname(full_output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def load_image_for_job(path_to_image, job_gamera_func):
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


def create_thumbnails(output_img, result):
    page = result.page
    job_module = result.job_item.job.module
    page.scale_value = 100. / max(output_img.ncols, output_img.nrows)
    scale_img_s = output_img.scale(page.scale_value, 0)
    scale_img_l = output_img.scale(page.scale_value * 10, 0)
    create_result_output_dirs(page.get_path_to_image('small', job_module))
    scale_img_s.save_PNG(page.get_path_to_image('small', job_module))
    scale_img_l.save_PNG(page.get_path_to_image('large', job_module))
