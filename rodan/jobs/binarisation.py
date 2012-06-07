import gamera.core

from celery.task import task

import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result


@task(name="binarisation.simple_binarise")
def simple_binarise(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    output_img = gamera.core.load_image(page_file_name).threshold(kwargs['threshold'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


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

    output_img = gamera.core.load_image(page_file_name).djvu_threshold(kwargs['smoothness'],
                        kwargs['max_block_size'],
                        kwargs['min_block_size'],
                        kwargs['block_factor'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.total_timestamp()


class SimpleThresholdBinarise(JobBase):
    name = 'Binarise (simple threshold)'
    slug = 'simple-binarise'
    input_type = JobType.IMAGE_GREY
    output_type = JobType.IMAGE_ONEBIT
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True
    parameters = {
        'threshold': 0
    }
    task = simple_binarise


class DJVUBinarise(JobBase):
    name = 'Binarise (DJVU)'
    slug = 'djvu-binarise'
    input_type = JobType.IMAGE_RGB
    output_type = JobType.IMAGE_ONEBIT
    description = 'Convert a RGB image to black and white.'
    show_during_wf_create = True
    parameters = {
        'smoothness': 0.2,
        'max_block_size': 512,
        'min_block_size': 64,
        'block_factor': 2
    }
    task = djvu_binarise
