from gamera.core import load_image
from gamera.toolkits.musicstaves import MusicStaves_rl_roach_tatem
from rodan.jobs.base import RodanTask

class RoachTatemRemoveStaffLines(RodanTask):
    name = 'Roach-Tatem Remove Staff Lines'
    author = "Ryan Bannon"
    description = 'Use Roach-Tatem staff line removal algorithm.'
    settings = {
        'title': 'Roach-Tatem settings',
        'type': 'object',
        'job_queue': 'Python3', 
        'properties': {
            'Number of lines per staff': {
                'type': 'integer',
                'default': 0,
                'minimum': 0,
                'description': 'Number of lines per staff. A value of 0 enables auto-detect. Better results if number of lines known.'
            }
        }
    }
    enabled = True
    category = "Gamera - Music Staves"
    interactive = False 

    input_port_types = [{
        'name': 'One-bit PNG image - original',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'One-bit PNG image - staff lines removed',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):

        fn_kwargs = {
            'num_lines': settings['Number of lines per staff'],
            'crossing_symbols': 'all',
            'resolution': 3.0,
            'debug': 0
        }
        original_image = load_image(inputs['One-bit PNG image - original'][0]['resource_path'])
        staff_finder = MusicStaves_rl_roach_tatem(original_image)
        staff_finder.remove_staves(**fn_kwargs)
        staff_finder.image.save_PNG(outputs['One-bit PNG image - staff lines removed'][0]['resource_path'])