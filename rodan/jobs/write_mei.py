import utils
from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='mei')
def combine_mei(mei_path, **kwargs):
    # Todo: This should take all of the MEI - one from each page in the
    # project - and combine it. We need to work out how to give a job
    # input from >1 page
    all_mei = ""
    
    return {
        'mei': all_mei
    }

class CombineMei(JobBase):
    name = 'Combine all MEI files'
    slug = 'combine-mei'
    input_type = JobType.CORRECTED_MEI
    output_type = JobType.END
    description = 'Make a single MEI file out of all images'
    show_during_wf_create = True
    is_automatic = True
    all_pages = True
    task = combine_mei
