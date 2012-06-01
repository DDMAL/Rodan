from rodan.models.jobs import JobType, JobBase
from tasks import tasks 

class SimpleThresholdBinarise(JobBase):
    input_type = JobType.IMAGE
    output_type = input_type
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        tv = kwargs['threshold']
        tasks.simple_binarise.delay(result_id,tv)

class DJVUBinarise(JobBase):
    input_type = JobType.IMAGE
    output_type = input_type
    description = 'Convert a RGB image to black and white.'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        smoothness = kwargs['smoothness']
        max_block_size = kwargs['max_block_size']
        min_block_size = kwargs['min_block_size']
        block_factor = kwargs['block_factor']
        tasks.djvu_binarise.delay(result_id,smoothness,max_block_size,min_block_size,block_factor)