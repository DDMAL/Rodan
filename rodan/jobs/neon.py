import utils

from django.conf import settings

from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs=None)
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
    outputs_image = False

    def get_context(self, page):
        return {
            'image': page.get_pre_bin_image_url(),
        }
