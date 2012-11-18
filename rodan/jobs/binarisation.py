import gamera.core
import gamera.plugins.threshold
from gamera.plugins.binarization import brink_threshold

from rodan.jobs.utils import rodan_task, load_image_for_job
from rodan.celery_models.jobtype import JobType
from rodan.celery_models.jobbase import JobBase
gamera.core.init_gamera()


@rodan_task(inputs='tiff')
def simple_binarise(image_filepath, **kwargs):
    input_image = load_image_for_job(image_filepath, gamera.plugins.threshold.threshold)
    output_image = input_image.threshold(kwargs['threshold'])

    return {
        'tiff': output_image
    }


@rodan_task(inputs="tiff")
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
    input_image = load_image_for_job(image_filepath, gamera.plugins.threshold.djvu_threshold)
    output_image = input_image.djvu_threshold( \
                        kwargs['smoothness'],
                        kwargs['max_block_size'],
                        kwargs['min_block_size'],
                        kwargs['block_factor'])

    return {
        'tiff': output_image
    }


@rodan_task(inputs='tiff')
def brink_binarise(image_filepath, **kwargs):
    input_image = load_image_for_job(image_filepath, brink_threshold)
    output_image = input_image.brink_threshold()

    return {
        'tiff': output_image
    }


class SimpleThresholdBinarise(JobBase):
    name = 'Binarise (simple threshold)'
    slug = 'simple-binarise'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Convert an image to black and white (simple threshold).'
    show_during_wf_create = True
    is_required = True
    parameters = {
        'threshold': 0
    }
    task = simple_binarise


class DJVUBinarise(JobBase):
    name = 'Binarise (DJVU)'
    slug = 'djvu-binarise'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Convert an image to black and white (DJVU algorithm).'
    show_during_wf_create = True
    is_required = True
    parameters = {
        'smoothness': 0.2,
        'max_block_size': 512,
        'min_block_size': 64,
        'block_factor': 2
    }
    task = djvu_binarise


class BrinkBinarise(JobBase):
    name = 'Binarise (Brink)'
    slug = 'brink-binarise'
    input_type = JobType.IMAGE
    output_type = JobType.BINARISED_IMAGE
    description = 'Convert an image to black and white (Brink algorithm).'
    show_during_wf_create = True
    is_required = True
    is_automatic = True
    task = brink_binarise
