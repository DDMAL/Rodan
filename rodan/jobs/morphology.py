import gamera.core
from gamera.plugins.morphology import despeckle

from celery.task import task

import utility
from rodan.models.jobs import JobType, JobBase
from rodan.models import Result


@task(name="morphology.despeckle")
def despeckle(result_id, **kwargs):
    """
      Removes connected components that are smaller than the given size.

      *size*
        The maximum number of pixels in each connected component that
        will be removed.

      This approach to finding connected components uses a pseudo-recursive
      descent, which gets around the hard limit of ~64k connected components
      per page in ``cc_analysis``.  Unfortunately, this approach is much
      slower as the connected components get large, so *size* should be
      kept relatively small.

      *size* == 1 is a special case and runs much faster, since it does not
      require recursion.
    """
    gamera.core.init_gamera()

    result = Result.objects.get(pk=result_id)
    page_file_name = result.page.get_latest_file(JobType.IMAGE_ONEBIT)

    output_img = gamera.core.load_image(page_file_name)  # must be OneBit, not using rodan load image (although it does prevent conversion to one bit)
    output_img.despeckle(kwargs['despeckle_value'])

    full_output_path = result.page.get_filename_for_job(result.job_item.job)
    utility.create_result_output_dirs(full_output_path)

    gamera.core.save_image(output_img, full_output_path)

    result.save_parameters(**kwargs)
    result.create_file(full_output_path, JobType.IMAGE_ONEBIT)
    result.update_end_total_time()


class Despeckle(JobBase):
    name = 'Despeckle'
    slug = 'despeckle'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.IMAGE_ONEBIT
    description = 'Despeckle a binarized image'
    show_during_wf_create = True
    parameters = {
        'despeckle_value': 100
    }
    task = despeckle
