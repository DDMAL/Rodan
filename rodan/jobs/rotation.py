from rodan.models import jobs

class Rotate(jobs.JobBase):
    name = 'Awesome rotation'
    description = 'I specified a name because I wanted to put in a space'
    slug = 'lolrotate'
    input_type = jobs.JobType.IMAGE
    output_type = input_type
    show_during_wf_create = True

    def on_post(self, **kwargs):
        pass
