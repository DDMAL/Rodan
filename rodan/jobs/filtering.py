import gamera.plugins.misc_filters

from rodan.jobs.utils import rodan_task, load_image_for_job
from rodan.celery_models.jobtype import JobType
from rodan.celery_models.jobbase import JobBase


@rodan_task(inputs='tiff')
def rank_filter(image_filepath, **kwargs):
    """
      *rank_val* (1, 2, ..., *k* * *k*)
        The rank of the windows pixels to select for the center. (k*k+1)/2 is
        equivalent to the median.

      *k* (3, 5 ,7, ...)
        The window size (must be odd).

      *border_treatment* (0, 1)
        When 0 ('padwhite'), window pixels outside the image are set to white.
        When 1 ('reflect'), reflecting boundary conditions are used.
    """
    input_image = load_image_for_job(image_filepath, gamera.plugins.misc_filters.rank)
    output_image = input_image.rank( \
        kwargs['rank_val'],
        kwargs['k'],
        kwargs['border_treatment'])

    return {
        'tiff': output_image
    }


class RankFilter(JobBase):
    name = 'Rank filter'
    slug = 'rank-filter'
    input_type = JobType.BINARISED_IMAGE
    output_type = JobType.RANKED_IMAGE
    description = 'Apply a rank filter to an image.'
    show_during_wf_create = True
    parameters = {
        'rank_val': 9,
        'k': 9,
        'border_treatment': 0
    }
    task = rank_filter
    is_automatic = True
    enabled = False
