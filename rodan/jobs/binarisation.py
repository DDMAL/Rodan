from rodan.models.jobs import JobType, JobBase
from tasks import tasks 

class Binarise(JobBase):
    input_type = JobType.IMAGE
    output_type = input_type
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        tv = kwargs['threshold_value']
        tasks.simple_binarise.delay(result_id,tv)
