from rodan.models.jobs import JobType, JobBase
from tasks import tasks


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
    task = tasks.despeckle