import gamera.core
from gamera.toolkits.lyric_extraction.plugins.border_lyric import correct_rotation

import utils
from rodan.models.jobs import JobType, JobBase


@utils.rodan_task(inputs='tiff')
def rotate(image_filepath, **kwargs):
    # load_image is called because rotate can accept any type of image
    input_image = gamera.core.load_image(image_filepath)
    angle = kwargs['angle']
    if angle != 0:
        output_image = input_image.rotate(angle)
    else:
        output_image = input_image

    return {
        'tiff': output_image
    }


class Rotate(JobBase):
    name = 'Rotate'
    slug = 'rotate'
    input_type = JobType.DESPECKLE_IMAGE
    output_type = JobType.ROTATED_IMAGE
    description = 'Rotate an image.'
    show_during_wf_create = True
    parameters = {
        'angle': 0
    }
    task = rotate

@utils.rodan_task(inputs='tiff')
def auto_rotate(image_filepath, **kwargs):
    input_image = utils.load_image_for_job(image_filepath, correct_rotation)
    output_image = input_image.correct_rotation(0)
    
    return {
        'tiff': output_image
    }

class AutoRotate(JobBase):
    name = 'Automatic Rotation'
    slug = 'auto-rotate'
    input_type = JobType.DESPECKLE_IMAGE
    output_type = JobType.ROTATED_IMAGE
    description = 'Automatically rotate an image.'
    show_during_wf_create = True
    is_automatic = True
    task = auto_rotate
