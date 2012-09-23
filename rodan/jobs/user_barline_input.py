import utils
import gamera
import json

from rodan.models.jobs import JobType, JobBase

@utils.rodan_task(inputs='tiff')
def barline_input(image_filepath, **kwargs):
    print kwargs
    return {
        'txt': kwargs['sequence']
    }

class BarlineInput(JobBase):
    input_type = JobType.BORDER_REMOVE_IMAGE
    output_type = JobType.STAFFGROUP_INPUT
    description = 'Describe the staff groups of a page'
    name = 'Barline Input'
    show_during_wf_create = True
    parameters = {
        'sequence': ''
    }
    task = barline_input
    
    def get_context(self, page):
        prev_page = page.get_previous_page()
        if prev_page:
            prev_txt_path = prev_page.get_latest_file_path('txt')
            if prev_txt_path:
                structure = open(prev_txt_path)
                return {
                    'previous_structure': structure.read()
                }
        return {
                    'previous_structure': None
        }
