from rodan.models.jobs import JobType, JobBase
from tasks import tasks 

class Rotate(JobBase):
    name = 'Rotate'
    slug = 'rotate'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.IMAGE_ONEBIT
    description = 'Rotates an image'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        angle = kwargs['angle']
        tasks.rotate.delay(result_id,angle)
