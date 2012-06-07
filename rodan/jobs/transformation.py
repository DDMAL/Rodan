from rodan.models.jobs import JobType, JobBase
from tasks import tasks


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
    task = tasks.rotate