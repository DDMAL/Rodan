import gamera.core
import gamera.toolkits.border_removal.plugins.border_removal
from PIL import Image, ImageEnhance

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def border_remover(image_filepath, **kwargs):
    input_image = utils.load_image_for_job(image_filepath, gamera.toolkits.border_removal.plugins.border_removal.border_removal)
    mask = input_image.border_removal()  # use defaults
    output_image = input_image.mask(mask)

    return {
        "tiff": output_image
    }


@utils.rodan_task(inputs='tiff')
def crop(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    scale_val = input_image.ncols / kwargs['imw']

    #added '- 1' to bottom right point coordinates because gamera goes 1 pixel over.
    output_image = input_image.subimage( \
        (kwargs['tlx'] * scale_val, kwargs['tly'] * scale_val),
        (kwargs['brx'] * scale_val - 1, kwargs['bry'] * scale_val - 1))

    return {
        "tiff": output_image
    }

@utils.rodan_task(inputs='tiff')
def luminance(image_filepath, **kwargs):
    input_image = Image.open(image_filepath)
    if kwargs['order'] == 0:
        output_image = ImageEnhance.Brightness(input_image).enhance(kwargs['brightness'])
        output_image = ImageEnhance.Contrast(output_image).enhance(kwargs['contrast'])
        output_image = ImageEnhance.Color(output_image).enhance(kwargs['colour'])
    elif kwargs['order'] == 1:
        output_image = ImageEnhance.Brightness(input_image).enhance(kwargs['brightness'])
        output_image = ImageEnhance.Color(output_image).enhance(kwargs['colour'])
        output_image = ImageEnhance.Contrast(output_image).enhance(kwargs['contrast'])
    elif kwargs['order'] == 2:
        output_image = ImageEnhance.Contrast(input_image).enhance(kwargs['contrast'])
        output_image = ImageEnhance.Brightness(output_image).enhance(kwargs['brightness'])
        output_image = ImageEnhance.Color(output_image).enhance(kwargs['colour'])
    elif kwargs['order'] == 3:
        output_image = ImageEnhance.Contrast(input_image).enhance(kwargs['contrast'])
        output_image = ImageEnhance.Color(output_image).enhance(kwargs['colour'])
        output_image = ImageEnhance.Brightness(output).enhance(kwargs['brightness'])
    elif kwargs['order'] == 4:
        output_image = ImageEnhance.Color(input_image).enhance(kwargs['colour'])
        output_image = ImageEnhance.Brightness(output_image).enhance(kwargs['brightness'])
        output_image = ImageEnhance.Contrast(output_image).enhance(kwargs['contrast'])
    else:
        output_image = ImageEnhance.Color(input_image).enhance(kwargs['colour'])
        output_image = ImageEnhance.Contrast(output_image).enhance(kwargs['contrast'])
        output_image = ImageEnhance.Brightness(output_image).enhance(kwargs['brightness'])
    return {
        "tiff": output_image
    }

class BorderRemoval(JobBase):
    name = 'Border removal'
    slug = 'border-remove'
    input_type = JobType.IMAGE
    output_type = JobType.BORDER_REMOVE_IMAGE
    description = 'Remove the borders of a greyscale image.'
    show_during_wf_create = True
    parameters = {

    }
    task = border_remover
    is_automatic = True


class Crop(JobBase):
    input_type = JobType.IMAGE
    output_type = JobType.BORDER_REMOVE_IMAGE
    description = 'Crop an image.'
    show_during_wf_create = True
    parameters = {
        'tlx': 0,
        'tly': 0,
        'brx': 0,
        'bry': 0,
        'imw': 1.0
    }
    task = crop

class Luminance(JobBase):
    input_type = JobType.IMAGE
    output_type = input_type
    description = 'Adjust the brightness, contrast, and colour enhancement of an RGB image.'
    show_during_wf_create = True
    parameters = {
        'brightness': 1.0,
        'contrast': 1.0,
        'colour': 1.0,
        'order': 0
    }
    task = luminance
    enabled = False
