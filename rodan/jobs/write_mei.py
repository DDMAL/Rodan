import utils
from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='tiff')
def combine_mei(image_filepath, **kwargs):
    input_image = utils.load_image_for_job(image_filepath, correct_rotation)
    output_image = input_image
    
    return {
        'tiff': output_image
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
