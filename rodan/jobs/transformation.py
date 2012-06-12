import gamera.core

from celery.task import task

import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result


@task(name="transformation.rotate")
def rotate(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    input_img = gamera.core.load_image(page_file_name)

    # accepts any type of image
    output_img = input_img.rotate(kwargs['angle'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    output_img.gamera.core.save_image(full_output_path)

    result.save_parameters(**kwargs)
    # same problem as for rank filter, need general purpose output type
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


class Rotate(JobBase):
    name = 'Rotate'
    slug = 'rotate'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.IMAGE_ONEBIT
    description = 'Rotates an image'
    show_during_wf_create = True
    parameters = {
        'angle': 0
    }
    task = rotate
