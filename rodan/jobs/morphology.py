from rodan.models.jobs import JobType, JobBase
from tasks import tasks


class Despeckle(JobBase):
    name = 'Despeckle'
    slug = 'despeckle'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.IMAGE_ONEBIT
    description = 'Despeckle a binarized image'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        dv = kwargs['despeckle_value']
        tasks.despeckle.delay(result_id, dv)
