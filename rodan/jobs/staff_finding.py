from rodan.models.jobs import JobType, JobBase
from tasks import tasks


class StaffFind(JobBase):
    name = 'Find staff lines'
    slug = 'staff-find'
    input_type = JobType.IMAGE_ONEBIT
    output_type = JobType.JSON
    description = 'Retrieves and outputs staff line point coordinates information in json format.'
    show_during_wf_create = True
    parameters = {
        'num_lines': 0,
        'scanlines': 20,
        'blackness': 0.8,
        'tolerance': -1
    }
    task = tasks.find_staves
