import gamera.core
from gamera.plugins.threshold import threshold
from gamera.plugins.threshold import djvu_threshold

import utils
from rodan.models.jobs import JobType, JobBase

gamera.core.init_gamera()

@utils.rodan_task(inputs='tiff')
def simple_binarise(image_filepath, **kwargs):
    input_image = utils.load_image_for_job(image_filepath, threshold)
    output_image = input_image.threshold(kwargs['threshold'])

    return {
        'tiff': output_image
    }


@utils.rodan_task(inputs="tiff")
def djvu_binarise(image_filepath, **kwargs):
    """
        *smoothness*
          The amount of effect that parent blocks have on their children
          blocks.  Higher values will result in more smoothness between
          blocks.  Expressed as a percentage between 0.0 and 1.0.

        *max_block_size*
          The size of the largest block to determine a threshold.

        *min_block_size*
          The size of the smallest block to determine a threshold.

        *block_factor*
          The number of child blocks (in each direction) per parent block.
          For instance, a *block_factor* of 2 results in 4 children per
          parent.
    """
    input_image = utils.load_image_for_job(image_filepath, djvu_threshold)
    output_image = input_image.djvu_threshold( \
                        kwargs['smoothness'],
                        kwargs['max_block_size'],
                        kwargs['min_block_size'],
                        kwargs['block_factor'])

    return {
        'tiff': output_image
    }


class SimpleThresholdBinarise(JobBase):
    name = 'Binarise (simple threshold)'
    slug = 'simple-binarise'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True
    parameters = {
        'threshold': 0
    }
    task = simple_binarise

class DJVUBinarise(JobBase):
    name = 'Binarise (DJVU)'
    slug = 'djvu-binarise'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Convert a RGB image to black and white.'
    show_during_wf_create = True
    parameters = {
        'smoothness': 0.2,
        'max_block_size': 512,
        'min_block_size': 64,
        'block_factor': 2
    }
    task = djvu_binarise
