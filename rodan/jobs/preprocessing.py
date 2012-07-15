import gamera.core
import gamera.toolkits.border_removal.plugins.border_removal

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


class BorderRemoval(JobBase):
    name = 'Border removal'
    slug = 'border-remove'
    input_type = JobType.IMAGE
    output_type = JobType.IMAGE
    description = 'Remove the borders of a greyscale image.'
    show_during_wf_create = True
    parameters = {

    }
    task = border_remover
    is_automatic = True


class Crop(JobBase):
    input_type = JobType.IMAGE
    output_type = input_type
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
