import utils
import gamera

from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='tiff')
def barfinder(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    scale_val = input_image.ncols / kwargs['imw']

    #added '- 1' to bottom right point coordinates because gamera goes 1 pixel over.
    output_image = input_image.subimage( \
        (kwargs['tlx'] * scale_val, kwargs['tly'] * scale_val),
        (kwargs['brx'] * scale_val - 1, kwargs['bry'] * scale_val - 1))

    return {
        "tiff": output_image
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

