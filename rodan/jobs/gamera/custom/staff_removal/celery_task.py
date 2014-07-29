from rodan.jobs.gamera.custom.gamera_custom_base import GameraCustomTask

from gamera.toolkits.musicstaves import MusicStaves_rl_roach_tatem


class RTStafflineRemovalTask(GameraCustomTask):
    max_retries = None
    name = 'gamera.custom.staff_removal.RT_staff_removal'

    settings = [{'default':0,'has_default':True,'rng':(-1048576,1048576),'name':'staffline_height','type':'int'},
                    {'default':0,'has_default':True,'rng':(-1048576,1048576),'name':'staffspace_height','type':'int'},
                    {'default':0,'has_default':True,'rng':(-1048576,1048576),'name':'num_lines','type':'int'},
                    {'default': 3,'has_default':True,'rng':(-1048576,1048576),'name':'resolution','type':'real'}]

    def process_image(self, task_image, settings):
        clsss_init_settings = dict( [(k, settings[k]) for k in ('staffline_height', 'staffspace_height')] )
        staffremover = MusicStaves_rl_roach_tatem(task_image, **clsss_init_settings)

        staffremoval_settings = dict( [(k, settings[k]) for k in ('num_lines', 'resolution')] )
        staffremover.remove_staves(**staffremoval_settings)

        return staffremover.image
