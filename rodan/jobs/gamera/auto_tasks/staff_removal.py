from rodan.jobs.base import RodanAutomaticTask
from gamera.core import load_image
from gamera.toolkits.musicstaves import MusicStaves_rl_roach_tatem


class RTStafflineRemovalTask(RodanAutomaticTask):
    name = 'gamera.auto_tasks.staff_removal.RT_staff_removal'
    author = "Deepanjan Roy"
    description = "Removes the staff lines usign Roach and Tatem Staffline removal algorithm."
    settings = {
        'type': 'object',
        'required': ['staffline_height', 'staffspace_height', 'num_lines', 'resolution'],
        'properties': {
            'staffline_height': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'staffspace_height': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'num_lines': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'resolution': {
                'type': 'number',
                'default': 3,
                'minimum': -1048576,
                'maximum': 1048576
            }
        }
    }

    enabled = True
    category = "Staff Removal"
    interactive = False

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])

        clsss_init_settings = dict( [(k, settings[k]) for k in ('staffline_height', 'staffspace_height')] )
        staffremover = MusicStaves_rl_roach_tatem(task_image, **clsss_init_settings)
        staffremoval_settings = dict( [(k, settings[k]) for k in ('num_lines', 'resolution')] )
        staffremover.remove_staves(**staffremoval_settings)
        result_image = staffremover.image

        result_image.save_PNG(outputs['output'][0]['resource_path'])
