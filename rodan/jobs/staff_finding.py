from rodan.models.jobs import JobType, JobBase
from tasks import tasks

class StaffFind(JobBase):
    name = 'Find staff lines'
    slug = 'staff-find'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.JSON
    description = 'Retrieves and outputs staff line point coordinates information in json format.'
    show_during_wf_create = True

    '''
    Requires a valid result_id and a threshold value
    '''
    def on_post(self, **kwargs):
        result_id = kwargs['result_id']
        num_lines = kwargs['num_lines']
        scanlines = kwargs['scanlines']
        blackness = kwargs['blackness']
        tolerance = kwargs['tolerance']
        tasks.find_staves.delay(result_id, num_lines, scanlines, blackness, tolerance)
