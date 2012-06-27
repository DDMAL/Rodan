import utils
from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs="jpg")
def neon(image_filepath, **kwargs):
    return {
        'mei': ''
    }

class Neon(JobBase):
    name = 'Neon'
    slug = 'neon'
    input_type = JobType.MEI_UNCORRECTED
    output_type = JobType.MEI_CORRECTED
    description = 'Correct OMR errors.'
    show_during_wf_create = False
    parameters = {
        'data': ''
    }
    task = neon
