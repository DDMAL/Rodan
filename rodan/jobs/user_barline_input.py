import utils
import gamera

from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='tiff')
def barline_input(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    scale_val = input_image.ncols / kwargs['imw']

    #added '- 1' to bottom right point coordinates because gamera goes 1 pixel over.
    output_image = input_image.subimage( \
        (kwargs['tlx'] * scale_val, kwargs['tly'] * scale_val),
        (kwargs['brx'] * scale_val - 1, kwargs['bry'] * scale_val - 1))

    return {
        "tiff": output_image
    }

class BarlineInput(JobBase):
    input_type = JobType.BORDER_REMOVE_IMAGE
    output_type = JobType.STAFFGROUP_INPUT
    description = 'Describe the staff groups of a page'
    name = 'Barline Input'
    show_during_wf_create = True
    parameters = {
    }
    task = barline_input
