import utils
import gamera

from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='tiff')
def barfinder(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    # Todo: do barfinder and output mei

    return {
        "tiff": input_image
    }

class BarFinder(JobBase):
    input_type = JobType.ROTATED_IMAGE
    output_type = JobType.MEI
    description = 'Find the bars in an image'
    name = 'Bar Finder'
    is_automatic = True
    show_during_wf_create = True
    parameters = {
    }
    task = barfinder

