import utils
import gamera

from rodan.models.jobs import JobType, JobBase
from barfinder_resources.barfinder import BarlineFinder
from barfinder_resources.meicreate import BarlineDataConverter

@utils.rodan_task(inputs=('tiff','txt'))
def barfinder(image_filepath, sg_hint_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)
    image_width = input_image.width
    image_height = input_image.height
    if input_image.resolution != 0:
        image_dpi = input_image.resolution
    else:
        # set a default image dpi of 72
        image_dpi = 72

    # get the staff group hint inputted by the user
    with open(sg_hint_filepath, 'r') as sg_file:
        sg_hint = sg_file.read()
        
    bar_finder = BarlineFinder()
    staff_bb, bar_bb = bar_finder.process_file(input_image, sg_hint, image_dpi)
    
    bar_converter = BarlineDataConverter(staff_bb, bar_bb)
    bar_converter.bardata_to_mei(sg_hint, image_filepath, image_width, image_height, image_dpi)
    mei_file = bar_converter.get_wrapped_mei()

    return {
        'mei': mei_file
    }

class BarFinder(JobBase):
    slug = 'bar-finder'
    input_type = JobType.ROTATED_IMAGE
    output_type = JobType.MEI
    description = 'Find the bars in an image'
    name = 'Bar Finder'
    is_automatic = True
    show_during_wf_create = True
    parameters = {
    }
    task = barfinder
    outputs_image = False
