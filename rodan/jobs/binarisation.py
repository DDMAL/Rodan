from rodan.models import jobs

class Binarise(jobs.JobBase):
    input_type = jobs.JobType.IMAGE
    output_type = input_type
    description = 'Convert a greyscale image to black and white.'
    show_during_wf_create = True

    def on_post(self, **kwargs):
        pass
