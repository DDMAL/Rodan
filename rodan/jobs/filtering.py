from rodan.models.jobs import JobType, JobBase
from tasks import tasks


class RankFilter(JobBase):
    name = 'Rank filter'
    slug = 'rank-filter'
    input_type = JobType.IMAGE_GREY
    output_type = input_type
    description = 'Applies rank filter on a binarized image'
    show_during_wf_create = True
    arguments = {
        'rank_val': 9,
        'k': 9,
        'border_treatment':0
    }
    task = tasks.rank_filter
