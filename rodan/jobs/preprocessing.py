import gamera.core
from gamera.toolkits import border_removal

from celery.task import task
import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result


@task(name="preprocessing.border_removal")
def border_remover(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    orig_image = gamera.core.load_image(page_file_name)

    mask = orig_image.border_removal()  # use defaults

    output_img = orig_image.mask(mask)

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


@task(name="preprocessing.crop")
def crop(result_id, **kwargs):
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE)

    orig_image = gamera.core.load_image(page_file_name)

    #added '- 1' to bottom right point coordinates because gamera goes 1 pixel over.
    output_img = orig_image.subimage((kwargs['top_left_x'], kwargs['top_left_y']), (kwargs['bottom_right_x'] - 1, kwargs['bottom_right_y'] - 1))

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)  # has to be same type as input..
    result.update_end_total_time()


class BorderRemoval(JobBase):
    name = 'Border Removal'
    slug = 'border-remove'
    input_type = JobType.IMAGE_GREY
    output_type = JobType.IMAGE_ONEBIT
    description = 'Removes the borders of a greyscale image.'
    show_during_wf_create = True
    parameters = {

    }
    task = border_removal


class Crop(JobBase):
    input_type = JobType.IMAGE_RGB
    output_type = input_type
    description = 'Crop an image.'
    show_during_wf_create = True
    parameters = {
        'top_left_x': 0,
        'top_left_y': 0,
        'bottom_right_x': 0,
        'bottom_right_y': 0,
    }
    task = crop
