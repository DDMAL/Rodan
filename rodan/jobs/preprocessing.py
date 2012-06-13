import gamera.core
from gamera.toolkits.border_removal.plugins.border_removal import border_removal

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def border_remover(image_filepath, **kwargs):
    input_image = utils.load_image_for_job(image_filepath, border_removal)
    mask = input_image.border_removal()  # use defaults
    output_image = input_image.mask(mask)

    return {
        "tiff": output_image
    }


@utils.rodan_task(inputs='tiff')
def crop(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    #added '- 1' to bottom right point coordinates because gamera goes 1 pixel over.
    output_image = input_image.subimage( \
        (kwargs['tlx'], kwargs['tly']),
        (kwargs['brx'] - 1, kwargs['bry'] - 1))

    return {
        "tiff": output_image
    }


class BorderRemoval(JobBase):
    name = 'Border Removal'
    slug = 'border-remove'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Removes the borders of a greyscale image.'
    show_during_wf_create = True
    parameters = {

    }
    task = border_removal


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
    }
    task = crop
