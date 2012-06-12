import gamera.core
from gamera.plugins.threshold import threshold
from gamera.plugins.threshold import djvu_threshold
from celery.task import task
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


"""
@task(name="binarisation.simple_binarise")
def simple_binarise(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    output_img = utils.load_image_for_job(page_file_name, threshold).threshold(kwargs['threshold'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utils.create_result_output_dirs(full_output_path)
    utils.create_thumbnails(output_img, result)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()
"""


@task(name="binarisation.djvu_threshold")
def djvu_binarise(result_id, **kwargs):
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
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    output_img = utils.load_image_for_job(page_file_name, djvu_threshold).djvu_threshold( \
                        kwargs['smoothness'],
                        kwargs['max_block_size'],
                        kwargs['min_block_size'],
                        kwargs['block_factor'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utils.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


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
