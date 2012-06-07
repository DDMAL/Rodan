from rodan.models.jobs import JobType, JobBase
from tasks import tasks


class SimpleThresholdBinarise(JobBase):
    name = 'Binarise (simple threshold)'
    slug = 'simple-binarise'
    input_type = JobType.IMAGE_GREY
    output_type = JobType.IMAGE_ONEBIT
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True
    parameters = {
        'threshold': 0
    }
    task = tasks.simple_binarise

class DJVUBinarise(JobBase):
    name = 'Binarise (DJVU)'
    slug = 'djvu-binarise'
    input_type = JobType.IMAGE_RGB
    output_type = JobType.IMAGE_ONEBIT
    description = 'Convert a RGB image to black and white.'
    show_during_wf_create = True
    parameters = {
        'smoothness': 0.2,
        'max_block_size': 512,
        'min_block_size': 64,
        'block_factor':2
    }
    task = tasks.djvu_binarise