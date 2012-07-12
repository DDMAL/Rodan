import gamera.core

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def rotate(image_filepath, **kwargs):
    # load_image is called because rotate can accept any type of image
    angle = kwargs['angle']
    if angle != 0:
        input_image = gamera.core.load_image(image_filepath)
        output_image = input_image.rotate(angle)
    else:
        output_image = "copy"

    return {
        'tiff': output_image
    }


class Rotate(JobBase):
    name = 'Rotate'
    slug = 'rotate'
    input_type = JobType.IMAGE
    output_type = JobType.IMAGE
    description = 'Rotate an image.'
    show_during_wf_create = True
    parameters = {
        'angle': 0
    }
    task = rotate
