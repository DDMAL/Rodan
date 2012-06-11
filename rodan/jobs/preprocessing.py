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
