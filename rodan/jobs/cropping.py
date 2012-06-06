from rodan.models import jobs

class Crop(jobs.JobBase):
    input_type = jobs.JobType.IMAGE_RGB
    output_type = input_type
    description = 'Crop an image.'
    show_during_wf_create = True

    def on_post(self, **kwargs):
        pass
